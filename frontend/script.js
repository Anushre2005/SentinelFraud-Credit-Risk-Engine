// API Base URL
const API_URL = window.location.origin;

// Chart instances
let scoreBreakdownChart = null;
let riskFactorsChart = null;

// Check if Chart.js is loaded
const chartJsLoaded = typeof Chart !== 'undefined';
console.log('Chart.js loaded:', chartJsLoaded);

// DOM Elements
const form = document.getElementById('assessmentForm');
const resultsSection = document.getElementById('resultsSection');
const loadingOverlay = document.getElementById('loadingOverlay');

// Form submit handler
form.addEventListener('submit', async (e) => {
    e.preventDefault();

    // Show loading
    loadingOverlay.classList.remove('hidden');
    resultsSection.classList.add('hidden');

    // Collect form data
    const formData = {
        user_id: document.getElementById('user_id').value,
        age: parseInt(document.getElementById('age').value),
        occupation: document.getElementById('occupation').value,
        monthly_income: parseFloat(document.getElementById('monthly_income').value),
        transaction_count_30d: parseInt(document.getElementById('transaction_count_30d').value),
        avg_transaction_amount: parseFloat(document.getElementById('avg_transaction_amount').value),
        location_risk_score: parseFloat(document.getElementById('location_risk_score').value),
        device_change_frequency: parseInt(document.getElementById('device_change_frequency').value),
        previous_fraud_flag: parseInt(document.getElementById('previous_fraud_flag').value),
        account_age_months: parseInt(document.getElementById('account_age_months').value),
        chargeback_count: parseInt(document.getElementById('chargeback_count').value)
    };

    try {
        const response = await fetch(`${API_URL}/credit/assess`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        displayResults(data, formData);

    } catch (error) {
        console.error('Error:', error);
        alert('Error analyzing credit risk. Please check the console for details.');
    } finally {
        loadingOverlay.classList.add('hidden');
    }
});

// Display results
function displayResults(data, formData) {
    resultsSection.classList.remove('hidden');

    // Scroll to results
    setTimeout(() => {
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);

    // Update score circle
    const score = data.decision.final_credit_score;
    const scoreNumber = document.getElementById('scoreNumber');
    const scoreProgress = document.getElementById('scoreProgress');

    scoreNumber.textContent = score;

    // Calculate progress (assuming max score is 1000)
    const maxScore = 1000;
    const percentage = Math.min(score / maxScore, 1);
    const circumference = 2 * Math.PI * 45;
    const offset = circumference - (percentage * circumference);

    scoreProgress.style.strokeDashoffset = offset;

    // Update risk band
    const riskValue = document.getElementById('riskValue');
    const riskBand = data.decision.risk_band.toLowerCase();
    riskValue.textContent = data.decision.risk_band;
    riskValue.className = `risk-value ${riskBand}`;

    // Update score interpretation
    const interpretation = document.getElementById('scoreInterpretation');
    interpretation.innerHTML = getScoreInterpretation(score, riskBand);

    // Create charts with error handling
    try {
        if (typeof Chart !== 'undefined') {
            setTimeout(() => {
                createScoreBreakdownChart(data);
                createRiskFactorsChart(data, formData);
            }, 100);
        } else {
            console.error('Chart.js not loaded');
            document.querySelector('.charts-section').innerHTML = `
                <div class="glass-card" style="padding: 40px; text-align: center; grid-column: 1/-1;">
                    <p style="color: var(--text-muted);">📊 Charts require an internet connection to load. Please refresh if charts don't appear.</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error creating charts:', error);
    }

    // Update applicant info
    const applicantInfo = document.getElementById('applicantInfo');
    applicantInfo.innerHTML = createInfoRows([
        ['User ID', data.applicant.user_id],
        ['Age', data.applicant.age],
        ['Occupation', capitalizeFirst(data.applicant.occupation)],
        ['Account Age', `${data.applicant.account_age_months} months`]
    ]);

    // Update rule scoring
    const ruleScoring = document.getElementById('ruleScoring');
    ruleScoring.innerHTML = createInfoRows([
        ['Base Score', data.rule_scoring.base_score, true],
        ['CTC Adjustment', formatAdjustment(data.rule_scoring.ctc_adjustment)],
        ['Address Adjustment', formatAdjustment(data.rule_scoring.address_adjustment)],
        ['Total Adjustment', formatAdjustment(data.rule_scoring.total_adjustment)],
        ['Final Rule Score', data.rule_scoring.final_rule_score, true]
    ]);

    // Update ML scoring
    const mlScoring = document.getElementById('mlScoring');
    mlScoring.innerHTML = createInfoRows([
        ['High Risk Probability', `${(data.ml_scoring.high_risk_probability * 100).toFixed(2)}%`],
        ['ML Score', data.ml_scoring.ml_score, true],
        ['Model AUC', data.ml_scoring.model_auc]
    ]);

    // Update network trust
    const networkTrust = document.getElementById('networkTrust');
    networkTrust.innerHTML = createInfoRows([
        ['Available', data.network_trust.available ? 'Yes' : 'No'],
        ['CTC Score', data.network_trust.ctc_score],
        ['Impact', data.network_trust.impact]
    ]);

    // Update address stability
    const addressStability = document.getElementById('addressStability');
    addressStability.innerHTML = createInfoRows([
        ['Available', data.address_stability.available ? 'Yes' : 'No'],
        ['Stability Score', data.address_stability.stability_score],
        ['Tenure Category', data.address_stability.tenure_category],
        ['Impact', data.address_stability.impact]
    ]);

    // Update compliance
    const compliance = document.getElementById('compliance');
    compliance.innerHTML = `
        <div class="info-row">
            <span class="info-label">Note</span>
        </div>
        <p style="color: var(--text-muted); font-size: 14px; line-height: 1.6;">
            ${data.compliance.note}
        </p>
        <div class="info-row" style="margin-top: 12px;">
            <span class="info-label">CTC Max Impact</span>
            <span class="info-value">${data.compliance.ctc_max_impact}</span>
        </div>
        <div class="info-row">
            <span class="info-label">Address Max Impact</span>
            <span class="info-value">${data.compliance.address_max_impact}</span>
        </div>
    `;

    // Always show recommendations
    const recommendationsSection = document.getElementById('recommendationsSection');
    recommendationsSection.classList.remove('hidden');
    recommendationsSection.classList.toggle('high-risk', riskBand === 'high');
    displayRecommendations(data, formData, riskBand);

    // Update meta info
    document.getElementById('assessmentId').textContent = data.assessment_id;
    document.getElementById('timestamp').textContent = formatTimestamp(data.timestamp);
}

// Get score interpretation text
function getScoreInterpretation(score, riskBand) {
    if (riskBand === 'low') {
        return `<strong style="color: var(--success);">Excellent!</strong> Your credit score of ${score} indicates a strong credit profile. You qualify for the best credit terms and lowest interest rates. Continue maintaining your healthy financial habits.`;
    } else if (riskBand === 'medium') {
        return `<strong style="color: var(--warning);">Fair</strong> - Your credit score of ${score} suggests moderate risk. You may qualify for credit but possibly at higher interest rates. Review the recommendations below to improve your score.`;
    } else {
        return `<strong style="color: var(--danger);">Needs Improvement</strong> - Your credit score of ${score} indicates higher risk. Credit applications may be declined or offered at premium rates. See the detailed recommendations below to improve your creditworthiness.`;
    }
}

// Create score breakdown chart
function createScoreBreakdownChart(data) {
    const canvas = document.getElementById('scoreBreakdownChart');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');

    if (scoreBreakdownChart) {
        scoreBreakdownChart.destroy();
    }

    scoreBreakdownChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Rule-Based Score', 'ML Score', 'Network Trust', 'Address Stability'],
            datasets: [{
                data: [
                    data.rule_scoring.final_rule_score,
                    data.ml_scoring.ml_score * 10,
                    data.network_trust.ctc_score * 100,
                    data.address_stability.stability_score * 100
                ],
                backgroundColor: [
                    'rgba(99, 102, 241, 0.8)',
                    'rgba(139, 92, 246, 0.8)',
                    'rgba(34, 211, 238, 0.8)',
                    'rgba(16, 185, 129, 0.8)'
                ],
                borderColor: [
                    'rgba(99, 102, 241, 1)',
                    'rgba(139, 92, 246, 1)',
                    'rgba(34, 211, 238, 1)',
                    'rgba(16, 185, 129, 1)'
                ],
                borderWidth: 2,
                hoverOffset: 10
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#94a3b8',
                        padding: 20,
                        font: { size: 12 }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(15, 23, 42, 0.9)',
                    titleColor: '#f1f5f9',
                    bodyColor: '#94a3b8',
                    borderColor: 'rgba(148, 163, 184, 0.2)',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: true
                }
            },
            cutout: '60%'
        }
    });
}

// Create risk factors chart
function createRiskFactorsChart(data, formData) {
    const canvas = document.getElementById('riskFactorsChart');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');

    if (riskFactorsChart) {
        riskFactorsChart.destroy();
    }

    // Calculate normalized risk factors (0-100 scale, higher = better)
    const factors = {
        'Income Level': Math.min(formData.monthly_income / 100, 100),
        'Account Age': Math.min(formData.account_age_months / 0.6, 100),
        'Location Safety': (1 - formData.location_risk_score) * 100,
        'Device Stability': Math.max(0, 100 - formData.device_change_frequency * 20),
        'Transaction Activity': Math.min(formData.transaction_count_30d * 2, 100),
        'Chargeback History': Math.max(0, 100 - formData.chargeback_count * 25)
    };

    riskFactorsChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: Object.keys(factors),
            datasets: [{
                label: 'Your Profile',
                data: Object.values(factors),
                backgroundColor: 'rgba(99, 102, 241, 0.2)',
                borderColor: 'rgba(99, 102, 241, 1)',
                borderWidth: 2,
                pointBackgroundColor: 'rgba(99, 102, 241, 1)',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgba(99, 102, 241, 1)'
            }, {
                label: 'Ideal Profile',
                data: [80, 80, 80, 80, 80, 80],
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                borderColor: 'rgba(16, 185, 129, 0.5)',
                borderWidth: 2,
                borderDash: [5, 5],
                pointRadius: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    min: 0,
                    max: 100,
                    ticks: {
                        stepSize: 20,
                        color: '#64748b',
                        backdropColor: 'transparent'
                    },
                    grid: {
                        color: 'rgba(148, 163, 184, 0.1)'
                    },
                    angleLines: {
                        color: 'rgba(148, 163, 184, 0.1)'
                    },
                    pointLabels: {
                        color: '#94a3b8',
                        font: { size: 11 }
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#94a3b8',
                        padding: 20,
                        font: { size: 12 }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(15, 23, 42, 0.9)',
                    titleColor: '#f1f5f9',
                    bodyColor: '#94a3b8',
                    padding: 12
                }
            }
        }
    });
}

// Create score components with progress bars
function createScoreComponents(data, formData) {
    const grid = document.getElementById('componentsGrid');

    const components = [
        {
            name: 'Base Rule Score',
            icon: '📊',
            value: data.rule_scoring.base_score,
            max: 500,
            description: 'Foundation score based on demographic and behavioral rules'
        },
        {
            name: 'ML Risk Assessment',
            icon: '🤖',
            value: 100 - (data.ml_scoring.high_risk_probability * 100),
            max: 100,
            description: `High risk probability: ${(data.ml_scoring.high_risk_probability * 100).toFixed(2)}%`
        },
        {
            name: 'Account Maturity',
            icon: '📅',
            value: Math.min(formData.account_age_months, 60),
            max: 60,
            description: `${formData.account_age_months} months of account history`
        },
        {
            name: 'Income Stability',
            icon: '💰',
            value: Math.min(formData.monthly_income / 50, 100),
            max: 100,
            description: `Monthly income: $${formData.monthly_income.toLocaleString()}`
        },
        {
            name: 'Location Trust',
            icon: '📍',
            value: (1 - formData.location_risk_score) * 100,
            max: 100,
            description: `Location risk score: ${formData.location_risk_score}`
        },
        {
            name: 'Device Consistency',
            icon: '📱',
            value: Math.max(0, 100 - formData.device_change_frequency * 20),
            max: 100,
            description: `Device changes: ${formData.device_change_frequency}`
        }
    ];

    grid.innerHTML = components.map(comp => {
        const percentage = (comp.value / comp.max) * 100;
        const status = percentage >= 70 ? 'good' : percentage >= 40 ? 'medium' : 'bad';

        return `
            <div class="component-item">
                <div class="component-header">
                    <span class="component-name">${comp.icon} ${comp.name}</span>
                    <span class="component-value">${typeof comp.value === 'number' ? comp.value.toFixed(0) : comp.value}</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill ${status}" style="width: ${percentage}%"></div>
                </div>
                <p class="component-description">${comp.description}</p>
            </div>
        `;
    }).join('');
}

// Display recommendations
function displayRecommendations(data, formData, riskBand) {
    const intro = document.getElementById('recommendationsIntro');
    const grid = document.getElementById('recommendationsGrid');
    const actionPlan = document.getElementById('actionPlan');
    const title = document.getElementById('recommendationsTitle');

    // Generate personalized recommendations based on weak areas
    const recommendations = generateRecommendations(data, formData, riskBand);

    // Update title and intro based on risk level
    if (riskBand === 'low') {
        title.textContent = '✨ Keep Up the Great Work! Tips to Maintain Your Score';
        intro.innerHTML = `🎉 <strong>Congratulations!</strong> Your credit score is excellent! Here are some tips to maintain your strong credit profile and potentially improve it even further.`;
        intro.style.background = 'rgba(16, 185, 129, 0.1)';
    } else if (riskBand === 'medium') {
        title.textContent = '📈 Personalized Recommendations to Improve Your Score';
        intro.innerHTML = `📊 <strong>Good Progress!</strong> Your credit profile shows room for improvement. Implementing the recommendations below can help you achieve a better score and access more favorable credit terms.`;
        intro.style.background = 'rgba(245, 158, 11, 0.1)';
    } else {
        title.textContent = '🚀 Action Plan to Rebuild Your Credit Score';
        intro.innerHTML = `⚠️ <strong>Important:</strong> Your credit assessment indicates elevated risk factors. Don't worry – with focused effort, you can significantly improve your credit profile. Below are personalized recommendations prioritized by potential impact.`;
        intro.style.background = 'rgba(239, 68, 68, 0.1)';
    }

    // Recommendation cards
    grid.innerHTML = recommendations.map(rec => `
        <div class="recommendation-card priority-${rec.priority}">
            <div class="recommendation-header">
                <span class="recommendation-icon">${rec.icon}</span>
                <span class="recommendation-title">${rec.title}</span>
                <span class="recommendation-priority ${rec.priority}">${rec.priority}</span>
            </div>
            <p class="recommendation-description">${rec.description}</p>
            <div class="recommendation-impact">
                <span>📈</span>
                <span>Expected Impact: ${rec.impact}</span>
            </div>
        </div>
    `).join('');

    // Action plan timeline - customize based on risk level
    if (riskBand === 'low') {
        actionPlan.innerHTML = `
            <div class="action-timeline">
                <div class="action-item">
                    <div class="action-period">Ongoing: Maintenance</div>
                    <ul class="action-tasks">
                        <li>Continue making all payments on time</li>
                        <li>Keep credit utilization below 30%</li>
                        <li>Review your credit report quarterly for errors</li>
                    </ul>
                </div>
                <div class="action-item">
                    <div class="action-period">Monthly: Monitoring</div>
                    <ul class="action-tasks">
                        <li>Track your credit score for any unexpected changes</li>
                        <li>Set up fraud alerts and credit monitoring</li>
                        <li>Review all financial statements for accuracy</li>
                    </ul>
                </div>
                <div class="action-item">
                    <div class="action-period">Annually: Optimization</div>
                    <ul class="action-tasks">
                        <li>Request credit limit increases to lower utilization</li>
                        <li>Evaluate if opening new credit makes sense</li>
                        <li>Check for any accounts that can be closed without impact</li>
                    </ul>
                </div>
            </div>
        `;
    } else {
        actionPlan.innerHTML = `
            <div class="action-timeline">
                <div class="action-item">
                    <div class="action-period">Week 1-2: Foundation</div>
                    <ul class="action-tasks">
                        <li>Review and dispute any errors on your credit report</li>
                        <li>Set up automatic payments for all existing accounts</li>
                        <li>Create a detailed budget tracking income and expenses</li>
                    </ul>
                </div>
                <div class="action-item">
                    <div class="action-period">Week 3-4: Building Habits</div>
                    <ul class="action-tasks">
                        <li>Reduce credit utilization below 30% if applicable</li>
                        <li>Avoid opening new credit accounts unnecessarily</li>
                        <li>Maintain consistent device and location patterns</li>
                    </ul>
                </div>
                <div class="action-item">
                    <div class="action-period">Month 2-3: Strengthening</div>
                    <ul class="action-tasks">
                        <li>Build emergency savings to avoid future financial stress</li>
                        <li>Consider becoming an authorized user on established accounts</li>
                        <li>Monitor your credit score monthly and track improvements</li>
                    </ul>
                </div>
            </div>
        `;
    }
}

// Generate personalized recommendations
function generateRecommendations(data, formData, riskBand) {
    const recommendations = [];

    // For low risk users, show maintenance tips
    if (riskBand === 'low') {
        recommendations.push({
            icon: '🏆',
            title: 'Maintain Payment History',
            description: 'Your excellent payment history is your biggest asset. Continue making all payments on time to protect your score.',
            impact: 'Maintains current score',
            priority: 'high'
        });

        recommendations.push({
            icon: '📊',
            title: 'Monitor Credit Utilization',
            description: 'Keep your credit utilization below 30% to maintain your excellent score. Lower is better!',
            impact: 'Protects score stability',
            priority: 'medium'
        });

        recommendations.push({
            icon: '🔒',
            title: 'Set Up Fraud Protection',
            description: 'Protect your excellent credit by enabling fraud alerts and credit monitoring services.',
            impact: 'Prevention of score drops',
            priority: 'low'
        });

        recommendations.push({
            icon: '📈',
            title: 'Consider Credit Limit Increases',
            description: 'Request credit limit increases periodically to improve your credit utilization ratio without increasing spending.',
            impact: '+5-15 potential points',
            priority: 'low'
        });
    } else {
        // For medium/high risk, show improvement recommendations

        // Check account age
        if (formData.account_age_months < 24) {
            recommendations.push({
                icon: '📅',
                title: 'Build Account History',
                description: 'Your account is relatively new. Keep your account active and in good standing to build a longer credit history. Avoid closing old accounts as length of history matters.',
                impact: '+30-50 points over 12 months',
                priority: 'high'
            });
        }

        // Check income level
        if (formData.monthly_income < 3000) {
            recommendations.push({
                icon: '💰',
                title: 'Increase Income Documentation',
                description: 'Consider documenting additional income sources such as freelance work, investments, or side businesses. A higher documented income improves your debt-to-income ratio.',
                impact: '+20-40 points',
                priority: 'medium'
            });
        }

        // Check location risk
        if (formData.location_risk_score > 0.3) {
            recommendations.push({
                icon: '📍',
                title: 'Improve Location Trust Score',
                description: 'Your location risk score is elevated. Ensure you\'re using consistent billing addresses and avoid frequent address changes. Register for mail at your primary residence.',
                impact: '+15-25 points',
                priority: 'medium'
            });
        }

        // Check device changes
        if (formData.device_change_frequency > 2) {
            recommendations.push({
                icon: '📱',
                title: 'Stabilize Device Usage',
                description: 'Frequent device changes can trigger fraud alerts. Use a primary device for financial transactions and enable biometric authentication for added security.',
                impact: '+10-20 points',
                priority: 'low'
            });
        }

        // Check chargebacks
        if (formData.chargeback_count > 0) {
            recommendations.push({
                icon: '🚫',
                title: 'Resolve Chargeback History',
                description: 'Past chargebacks significantly impact your score. Ensure all disputes are properly documented and work with merchants to resolve any ongoing issues.',
                impact: '+40-60 points',
                priority: 'high'
            });
        }

        // Check previous fraud
        if (formData.previous_fraud_flag === 1) {
            recommendations.push({
                icon: '🛡️',
                title: 'Clear Fraud Flags',
                description: 'Previous fraud flags severely impact creditworthiness. Contact your financial institutions to understand the flag, provide documentation to clear it, and consider identity theft protection.',
                impact: '+50-100 points',
                priority: 'high'
            });
        }

        // Check transaction activity
        if (formData.transaction_count_30d < 10) {
            recommendations.push({
                icon: '💳',
                title: 'Increase Account Activity',
                description: 'Low transaction activity may indicate dormant accounts. Use your accounts regularly for small purchases to demonstrate active, responsible usage.',
                impact: '+10-15 points',
                priority: 'low'
            });
        }

        // ML risk recommendations
        if (data.ml_scoring.high_risk_probability > 0.3) {
            recommendations.push({
                icon: '🤖',
                title: 'Address ML-Detected Risk Patterns',
                description: 'Our machine learning model detected patterns associated with higher risk. Focus on consistent financial behavior, regular payments, and avoiding unusual transaction patterns.',
                impact: '+25-45 points',
                priority: 'high'
            });
        }
    }

    // General recommendations for all users
    recommendations.push({
        icon: '📊',
        title: 'Monitor Your Credit Regularly',
        description: 'Set up credit monitoring alerts and review your credit report quarterly. Early detection of issues allows for faster resolution and prevents score damage.',
        impact: 'Prevention of score drops',
        priority: 'low'
    });

    // Sort by priority
    const priorityOrder = { high: 0, medium: 1, low: 2 };
    recommendations.sort((a, b) => priorityOrder[a.priority] - priorityOrder[b.priority]);

    return recommendations.slice(0, 6); // Return top 6 recommendations
}

// Helper functions
function createInfoRows(rows) {
    return rows.map(([label, value, highlight]) => `
        <div class="info-row">
            <span class="info-label">${label}</span>
            <span class="info-value${highlight ? ' highlight' : ''}">${value}</span>
        </div>
    `).join('');
}

function formatAdjustment(value) {
    if (value === 0) return '0';
    return value > 0 ? `+${value}` : value.toString();
}

function capitalizeFirst(str) {
    return str.charAt(0).toUpperCase() + str.slice(1).replace('_', ' ');
}

function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}
