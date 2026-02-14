document.addEventListener('DOMContentLoaded', () => {
    lucide.createIcons();
    setupEventListeners();
});

// --- State Management ---
let allQuestions = [];
let selectedQuestions = new Set();

// --- Elements ---
const generateBtn = document.getElementById('generate-aptitude-btn');
const jdInput = document.getElementById('jd-input');
const fileInput = document.getElementById('file-upload');
const fileNameDisplay = document.getElementById('file-name');
const loader = document.getElementById('loader');

const selectionSection = document.getElementById('selection-section');
const questionsList = document.getElementById('questions-list');
const selectedCount = document.getElementById('selected-count');
const selectAllCheckbox = document.getElementById('select-all-checkbox');
const doneBtn = document.getElementById('done-btn');

const finalResultSection = document.getElementById('final-result-section');
const finalAptitudeList = document.getElementById('final-aptitude-list');
const copyBtn = document.getElementById('copy-btn');
const downloadPdfBtn = document.getElementById('download-pdf-btn');
const emailBtn = document.getElementById('email-btn');

// Modal Elements
const emailModal = document.getElementById('email-modal');
const closeEmailModal = document.getElementById('close-email-modal');
const cancelEmailBtn = document.getElementById('cancel-email');
const confirmSendEmailBtn = document.getElementById('confirm-send-email');
const receiverEmailsInput = document.getElementById('receiver-emails');

// Analysis Elements
const viewAnalysisBtn = document.getElementById('view-analysis-btn');
const analysisDashboard = document.getElementById('analysis-dashboard-section');
const mainGeneratorCard = document.querySelector('.generator-layout .main-card:first-child');
const jobRolesView = document.getElementById('job-roles-view');
const candidateDetailsView = document.getElementById('candidate-details-view');
const detailJobTitleText = document.getElementById('detail-job-title');
const candidatesTbody = document.getElementById('candidates-tbody');

// --- Setup ---
function setupEventListeners() {
    // File Upload handling
    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            fileNameDisplay.textContent = file.name;
            const reader = new FileReader();
            reader.onload = (re) => {
                jdInput.value = re.target.result;
            };
            reader.readAsText(file);
        }
    });

    // Step 1: Generate Real Questions from Backend
    generateBtn.addEventListener('click', async () => {
        const jdText = jdInput.value.trim();
        if (!jdText) {
            alert("Please paste a Job Description or upload a file first.");
            return;
        }

        showLoader(true);
        
        try {
            const response = await fetch('http://127.0.0.1:8002/generate-aptitude', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ jd_text: jdText })
            });

            if (!response.ok) throw new Error("Failed to generate questions");

            const data = await response.json();
            allQuestions = data.questions;
            
            renderQuestionsToSelect();
            showLoader(false);
            showSection(selectionSection);
            selectionSection.scrollIntoView({ behavior: 'smooth' });
        } catch (error) {
            console.error(error);
            alert("Error connecting to backend AI. Please ensure the backend server is running on port 8002.");
            showLoader(false);
        }
    });

    // Step 2: Confirmation
    doneBtn.addEventListener('click', () => {
        if (selectedQuestions.size === 0) {
            alert("Please select at least one question.");
            return;
        }
        renderFinalList();
        showSection(finalResultSection);
        finalResultSection.scrollIntoView({ behavior: 'smooth' });
    });

    // Final: Actions
    copyBtn.addEventListener('click', copyToClipboard);
    downloadPdfBtn.addEventListener('click', simulatePdfDownload);
    
    // Modal Events
    emailBtn.addEventListener('click', () => {
        emailModal.classList.remove('hidden');
    });

    closeEmailModal.addEventListener('click', () => emailModal.classList.add('hidden'));
    cancelEmailBtn.addEventListener('click', () => emailModal.classList.add('hidden'));
    
    confirmSendEmailBtn.addEventListener('click', async () => {
        const emailsString = receiverEmailsInput.value.trim();
        if(!emailsString) {
            alert("Please enter at least one email address.");
            return;
        }

        // Dynamically get Job Title from JD text (looking for 'JOB TITLE: ...')
        const jdValue = jdInput.value;
        const jobTitleMatch = jdValue.match(/JOB TITLE:\s*(.*)/i);
        let jobTitle = "Technical Assessment";
        
        if (jobTitleMatch && jobTitleMatch[1]) {
            jobTitle = jobTitleMatch[1].trim();
        } else {
            // Fallback to header if JD parsing fails
            const headerTitle = document.querySelector('.main-generator h1')?.textContent.replace('Generated Questions for: ', '').trim();
            if (headerTitle) jobTitle = headerTitle;
        }

        const emailsArray = emailsString.split(',').map(e => e.trim()).filter(e => e);
        
        // Use current window location to generate link (helps in mobile/network testing)
        const baseUrl = window.location.origin + "/Aptitude_Generator/frontend/test.html";
        const assessmentLink = `${baseUrl}?role=${encodeURIComponent(jobTitle)}&token=${Math.random().toString(36).substr(2, 9)}`;
        
        // Show loading state on button
        confirmSendEmailBtn.innerHTML = '<span>Sending...</span><i class="ai-spinner-small"></i>';
        confirmSendEmailBtn.disabled = true;

        try {
            const response = await fetch('http://127.0.0.1:8002/send-assessment', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    emails: emailsArray,
                    job_title: jobTitle,
                    questions_count: selectedQuestions.size,
                    assessment_link: assessmentLink,
                    questions: Array.from(selectedQuestions)
                })
            });

            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.detail || "Failed to send emails");
            }

            await showCustomAlert("✅ Success!", `Assessments have been delivered to ${emailsArray.length} candidates successfully.`);
            emailModal.classList.add('hidden');
            receiverEmailsInput.value = '';
        } catch (error) {
            console.error(error);
            showCustomAlert("❌ Error", "Failed to complete request: " + error.message);
        } finally {
            confirmSendEmailBtn.innerHTML = '<span>Send Assessment</span><i data-lucide="send"></i>';
            confirmSendEmailBtn.disabled = false;
            lucide.createIcons();
        }
    });

    // Analysis Events
    viewAnalysisBtn.addEventListener('click', showAnalysisDashboard);

    // Select All Toggle
    selectAllCheckbox.addEventListener('change', () => {
        const isChecked = selectAllCheckbox.checked;
        const items = questionsList.querySelectorAll('.question-item');
        
        selectedQuestions.clear();
        items.forEach((item, index) => {
            const qObj = allQuestions[index];
            const checkbox = item.querySelector('.q-real-checkbox');
            
            if (isChecked) {
                item.classList.add('selected');
                checkbox.checked = true;
                selectedQuestions.add(qObj);
            } else {
                item.classList.remove('selected');
                checkbox.checked = false;
            }
        });
        updateCount();
    });
}

// --- Logic Functions ---

function generateMockQuestions() {
    // In a real scenario, this data would come from the backend AI
    allQuestions = [
        "Explain the difference between synchronous and asynchronous programming in Python.",
        "How do you handle state management in a large-scale React application?",
        "Describe the CAP theorem and its implications for distributed databases.",
        "What are the primary differences between REST and GraphQL APIs?",
        "How would you optimize a slow-running SQL query?",
        "Explain the concept of 'Dependency Injection' and why it is useful.",
        "What is the role of a JWT in authentication, and how does it work?",
        "Describe the microservices architecture and one of its main drawbacks.",
        "How do you ensure data security while building a public-facing API?",
        "Explain the lifecycle of a request in a typical web framework."
    ];

    renderQuestionsToSelect();
}

const NEON_INNER_HTML = `
    <div class="neon-checkbox__frame">
        <div class="neon-checkbox__box">
            <div class="neon-checkbox__check-container">
                <svg viewBox="0 0 24 24" class="neon-checkbox__check">
                    <path d="M3,12.5l7,7L21,5"></path>
                </svg>
            </div>
            <div class="neon-checkbox__glow"></div>
            <div class="neon-checkbox__borders">
                <span></span><span></span><span></span><span></span>
            </div>
        </div>
        <div class="neon-checkbox__effects">
            <div class="neon-checkbox__particles">
                <span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span>
            </div>
            <div class="neon-checkbox__rings">
                <div class="ring"></div><div class="ring"></div><div class="ring"></div>
            </div>
            <div class="neon-checkbox__sparks">
                <span></span><span></span><span></span><span></span>
            </div>
        </div>
    </div>
`;

function renderQuestionsToSelect() {
    questionsList.innerHTML = '';
    selectedQuestions.clear();
    selectAllCheckbox.checked = false;
    updateCount();

    allQuestions.forEach((qObj, index) => {
        const item = document.createElement('div');
        item.className = 'question-item';
        
        const questionText = typeof qObj === 'string' ? qObj : qObj.question;
        const options = qObj.options || [];
        const qId = qObj.id || `Q${index + 1}`;

        let optionsHtml = '';
        if (options.length > 0) {
            optionsHtml = `
                <div class="options-grid">
                    ${options.map((opt, i) => `<div class="option-box"><span>${String.fromCharCode(65 + i)})</span> ${opt}</div>`).join('')}
                </div>
            `;
        }

        item.innerHTML = `
            <div class="q-checkbox-wrapper">
                <label class="neon-checkbox">
                    <input type="checkbox" class="q-real-checkbox">
                    ${NEON_INNER_HTML}
                </label>
            </div>
            <div class="q-content">
                <div class="q-id-text">${qId}: ${questionText}</div>
                ${optionsHtml}
            </div>
        `;

        const checkbox = item.querySelector('.q-real-checkbox');

        item.addEventListener('click', (e) => {
            // Prevent double toggle if clicking label/input directly
            if (e.target.tagName === 'INPUT') return;
            
            checkbox.checked = !checkbox.checked;
            toggleQuestionSelection();
        });

        checkbox.addEventListener('change', toggleQuestionSelection);

        function toggleQuestionSelection() {
            if (checkbox.checked) {
                item.classList.add('selected');
                selectedQuestions.add(qObj);
            } else {
                item.classList.remove('selected');
                selectedQuestions.delete(qObj);
            }
            // Update Select All checkbox state
            selectAllCheckbox.checked = selectedQuestions.size === allQuestions.length;
            updateCount();
        }

        questionsList.appendChild(item);
    });
    lucide.createIcons();
}

function updateCount() {
    selectedCount.textContent = selectedQuestions.size;
}

function renderFinalList() {
    finalAptitudeList.innerHTML = '';
    let index = 1;
    selectedQuestions.forEach(qObj => {
        const questionText = typeof qObj === 'string' ? qObj : qObj.question;
        const options = qObj.options || [];
        const answer = qObj.answer || "";

        const container = document.createElement('div');
        container.className = 'final-q-card';
        
        let optionsHtml = '';
        if (options.length > 0) {
            optionsHtml = `
                <div class="final-options-grid">
                    ${options.map((opt, i) => `<div class="final-opt"><span>${String.fromCharCode(65 + i)})</span> ${opt}</div>`).join('')}
                </div>
            `;
        }

        container.innerHTML = `
            <div class="final-q-text"><strong>Q${index++}:</strong> ${questionText}</div>
            ${optionsHtml}
            <div class="final-answer">Correct Answer: ${answer}</div>
        `;
        finalAptitudeList.appendChild(container);
    });
}

function showLoader(show) {
    if (show) loader.classList.remove('hidden');
    else loader.classList.add('hidden');
}

function showSection(section) {
    section.classList.remove('hidden');
}

function copyToClipboard() {
    const text = Array.from(selectedQuestions)
        .map((qObj, i) => {
            const q = typeof qObj === 'string' ? qObj : qObj.question;
            const opts = (qObj.options || []).map((o, idx) => `${String.fromCharCode(65 + idx)}) ${o}`).join('\n');
            const ans = qObj.answer ? `\nCorrect Answer: ${qObj.answer}` : "";
            return `Q${i+1}: ${q}\n${opts}${ans}`;
        })
        .join('\n\n---\n\n');
    
    navigator.clipboard.writeText(text).then(() => {
        const originalText = copyBtn.innerHTML;
        copyBtn.innerHTML = '<i data-lucide="check"></i> Copied!';
        lucide.createIcons();
        setTimeout(() => {
            copyBtn.innerHTML = originalText;
            lucide.createIcons();
        }, 2000);
    });
}

function simulatePdfDownload() {
    alert("In the full implementation, this will generate a formatted PDF of your selected questions.");
}

// --- Custom Modal Helper ---
const confirmModal = document.getElementById('confirm-modal');
const confirmTitle = document.getElementById('confirm-title');
const confirmMsg = document.getElementById('confirm-message');
const confirmOkBtn = document.getElementById('confirm-ok-btn');
const confirmCancelBtn = document.getElementById('confirm-cancel-btn');
const closeConfirmBtn = document.getElementById('close-confirm');

function showCustomAlert(title, message) {
    confirmTitle.textContent = title;
    confirmMsg.textContent = message;
    confirmCancelBtn.classList.add('hidden');
    confirmModal.classList.remove('hidden');
    return new Promise((resolve) => {
        const handleOk = () => {
            confirmModal.classList.add('hidden');
            confirmOkBtn.removeEventListener('click', handleOk);
            resolve(true);
        };
        confirmOkBtn.addEventListener('click', handleOk);
    });
}

function showCustomConfirm(title, message) {
    confirmTitle.textContent = title;
    confirmMsg.textContent = message;
    confirmCancelBtn.classList.remove('hidden');
    confirmModal.classList.remove('hidden');
    return new Promise((resolve) => {
        const handleOk = () => {
            confirmModal.classList.add('hidden');
            cleanup();
            resolve(true);
        };
        const handleCancel = () => {
            confirmModal.classList.add('hidden');
            cleanup();
            resolve(false);
        };
        const cleanup = () => {
            confirmOkBtn.removeEventListener('click', handleOk);
            confirmCancelBtn.removeEventListener('click', handleCancel);
            closeConfirmBtn.removeEventListener('click', handleCancel);
        };
        confirmOkBtn.addEventListener('click', handleOk);
        confirmCancelBtn.addEventListener('click', handleCancel);
        closeConfirmBtn.addEventListener('click', handleCancel);
    });
}

window.showCustomAlert = showCustomAlert;
window.showCustomConfirm = showCustomConfirm;

// --- Helper: Format Date as DD/MM/YYYY : HH/MM/SS ---
function formatProctoringDate(timestamp) {
    if (!timestamp) return '-';
    const d = new Date(timestamp * 1000);
    const pad = (n) => n.toString().padStart(2, '0');
    
    const date = `${pad(d.getDate())}/${pad(d.getMonth() + 1)}/${d.getFullYear()}`;
    const time = `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
    
    return `${date} : ${time}`;
}

async function showAnalysisDashboard() {
    mainGeneratorCard.classList.add('hidden');
    selectionSection.classList.add('hidden');
    finalResultSection.classList.add('hidden');
    analysisDashboard.classList.remove('hidden');

    const rolesTbody = document.getElementById('job-roles-tbody');
    const emptyState = document.getElementById('empty-state');
    const table = document.querySelector('.modern-table');
    const totalSentStat = document.getElementById('total-tests-stat');
    const completionRateStat = document.getElementById('completion-rate-stat');

    // Reset view
    rolesTbody.innerHTML = '';
    totalSentStat.textContent = '0';
    completionRateStat.textContent = '0%';
    emptyState.classList.add('hidden');
    table.classList.remove('hidden');

    try {
        const response = await fetch('http://127.0.0.1:8002/get-analytics');
        if (!response.ok) throw new Error("Backend not reachable");
        
        const db = await response.json();
        
        if (!db.assessments || db.assessments.length === 0) {
            table.classList.add('hidden');
            emptyState.classList.remove('hidden');
            return;
        }

        // Update Stats
        const totalSent = db.assessments.reduce((acc, curr) => acc + curr.emails.length, 0);
        totalSentStat.textContent = totalSent;
        
        const totalAttempted = db.submissions.length;
        const rate = totalSent > 0 ? Math.round((totalAttempted / totalSent) * 100) : 0;
        completionRateStat.textContent = rate + '%';

        // Update Header for Date Column
        const thead = document.querySelector('#roles-table-header');
        if (thead && !thead.innerHTML.includes('SENT DATE')) {
            const actionsTh = thead.lastElementChild;
            const dateTh = document.createElement('th');
            dateTh.textContent = 'SENT DATE';
            thead.insertBefore(dateTh, actionsTh);
        }

        // Render Roles Table
        rolesTbody.innerHTML = db.assessments.map(a => {
            const attempted = db.submissions.filter(s => s.token === a.token).length;
            const pending = a.emails.length - attempted;
            const sentDate = formatProctoringDate(a.timestamp);
            
            return `
                <tr>
                    <td onclick="viewCandidateDetails('${a.job_title}', '${a.token}')">${a.job_title}</td>
                    <td onclick="viewCandidateDetails('${a.job_title}', '${a.token}')">${a.emails.length}</td>
                    <td onclick="viewCandidateDetails('${a.job_title}', '${a.token}')">${attempted}</td>
                    <td onclick="viewCandidateDetails('${a.job_title}', '${a.token}')">${pending}</td>
                    <td onclick="viewCandidateDetails('${a.job_title}', '${a.token}')">${sentDate}</td>
                    <td>
                        <div class="actions-cell">
                            <button class="glass-btn sm" onclick="viewCandidateDetails('${a.job_title}', '${a.token}')">View Details</button>
                            <button class="delete-btn" onclick="event.stopPropagation(); deleteAssessment('${a.token}')" title="Delete Assessment">
                                <i data-lucide="trash-2"></i>
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        }).join('');
        lucide.createIcons();
    } catch (error) {
        console.error("Failed to fetch analytics:", error);
        table.classList.add('hidden');
        emptyState.querySelector('p').textContent = "Unable to connect to service. Please ensure the backend server is running.";
        emptyState.classList.remove('hidden');
    }
}

window.deleteAssessment = async function(token) {
    const confirmed = await showCustomConfirm("Delete Assessment", "Are you sure you want to delete this assessment and all its submission data? This cannot be undone.");
    if (!confirmed) return;

    try {
        const response = await fetch(`http://127.0.0.1:8002/delete-assessment/${token}`, { method: 'DELETE' });
        if (response.ok) {
            showAnalysisDashboard(); // Refresh
        } else {
            showCustomAlert("Error", "Failed to delete assessment.");
        }
    } catch (error) {
        showCustomAlert("Error", "Connection error. Could not delete.");
    }
}

window.hideAnalysis = function() {
    analysisDashboard.classList.add('hidden');
    mainGeneratorCard.classList.remove('hidden');
}

window.viewCandidateDetails = async function(jobTitle, token) {
    detailJobTitleText.textContent = jobTitle;
    jobRolesView.classList.add('hidden');
    candidateDetailsView.classList.remove('hidden');
    
    try {
        const response = await fetch('http://127.0.0.1:8002/get-analytics');
        const db = await response.json();
        
        const assessment = db.assessments.find(a => a.token === token);
        const submissions = db.submissions.filter(s => s.token === token);

        candidatesTbody.innerHTML = assessment.emails.map(email => {
            const sub = submissions.find(s => s.email === email);
            let status = sub ? 'Attempted' : 'Pending';
            let statusClass = status.toLowerCase();
            
            if (sub && sub.suspicious === "Unwanted Move") {
                status = "Unwanted Move";
                statusClass = "rejected"; 
            }

            const score = sub ? `${sub.score}/${sub.total}` : '-';
            const date = sub ? formatProctoringDate(sub.timestamp) : '-';
            
            return `
                <tr>
                    <td>${email}</td>
                    <td><span class="status-tag ${statusClass}">${status}</span></td>
                    <td>${score}</td>
                    <td>${date}</td>
                </tr>
            `;
        }).join('');
    } catch (error) {
        console.error("Failed to fetch candidate details:", error);
    }
    lucide.createIcons();
}

window.backToRoles = function() {
    candidateDetailsView.classList.add('hidden');
    jobRolesView.classList.remove('hidden');
}
