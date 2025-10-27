// 복리 계산기 로직
function calculateCompoundInterest() {
    // 입력값 가져오기
    const initialAmount = parseFloat(document.getElementById('initial-amount').value) || 0;
    const monthlyInvestment = parseFloat(document.getElementById('monthly-investment').value) || 0;
    const period = parseFloat(document.getElementById('period').value) || 0;
    const interestRate = parseFloat(document.getElementById('interest-rate').value) || 0;

    if (initialAmount <= 0 || period <= 0 || interestRate <= 0) {
        alert('모든 값을 올바르게 입력해주세요.');
        return;
    }

    // 복리 계산
    const monthlyRate = interestRate / 100 / 12;
    const totalMonths = period * 12;
    
    // 초기 투자액의 복리 계산
    const initialFutureValue = initialAmount * Math.pow(1 + monthlyRate, totalMonths);
    
    // 월 투자액의 복리 계산 (연금 공식)
    let monthlyFutureValue = 0;
    if (monthlyInvestment > 0) {
        monthlyFutureValue = monthlyInvestment * 
            (Math.pow(1 + monthlyRate, totalMonths) - 1) / monthlyRate;
    }
    
    const finalAmount = initialFutureValue + monthlyFutureValue;
    const totalInvestment = initialAmount + (monthlyInvestment * totalMonths);
    const totalProfit = finalAmount - totalInvestment;

    // 결과 표시
    document.getElementById('total-investment').textContent = formatCurrency(totalInvestment);
    document.getElementById('total-profit').textContent = formatCurrency(totalProfit);
    document.getElementById('final-amount').textContent = formatCurrency(finalAmount);

    // 72의 법칙 계산
    const doubleTime = 72 / interestRate;
    document.getElementById('rule-result').innerHTML = 
        `연 ${interestRate}% 수익률로 투자하면 약 <strong>${doubleTime.toFixed(1)}년</strong>만에 원금이 2배가 됩니다.`;

    // 차트 업데이트
    updateCompoundChart(initialAmount, monthlyInvestment, period, interestRate);

    // 보고서 데이터 업데이트
    updateReportData({
        startYear: new Date().getFullYear(),
        period: period,
        targetReturn: interestRate,
        projectedAssets: finalAmount
    });
}

// 차트 업데이트 함수
function updateCompoundChart(initial, monthly, years, rate) {
    const ctx = document.getElementById('compound-chart').getContext('2d');
    
    // 기존 차트 삭제
    if (window.compoundChart) {
        window.compoundChart.destroy();
    }

    // 연도별 데이터 계산
    const labels = [];
    const principalData = [];
    const totalData = [];
    
    const monthlyRate = rate / 100 / 12;
    
    for (let year = 0; year <= years; year++) {
        labels.push(year + '년');
        
        const months = year * 12;
        const principalAmount = initial + (monthly * months);
        
        let totalAmount = initial * Math.pow(1 + monthlyRate, months);
        if (monthly > 0 && months > 0) {
            totalAmount += monthly * (Math.pow(1 + monthlyRate, months) - 1) / monthlyRate;
        }
        
        principalData.push(principalAmount);
        totalData.push(totalAmount);
    }

    // 차트 생성
    window.compoundChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: '투자원금',
                data: principalData,
                borderColor: '#ff6b6b',
                backgroundColor: 'rgba(255, 107, 107, 0.1)',
                fill: true,
                tension: 0.4
            }, {
                label: '복리수익 포함',
                data: totalData,
                borderColor: '#4ecdc4',
                backgroundColor: 'rgba(78, 205, 196, 0.1)',
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return formatCurrency(value);
                        }
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            },
            tooltips: {
                callbacks: {
                    label: function(context) {
                        return context.dataset.label + ': ' + formatCurrency(context.parsed.y);
                    }
                }
            }
        }
    });
}

// 통화 형식으로 변환
function formatCurrency(amount) {
    return new Intl.NumberFormat('ko-KR', {
        style: 'currency',
        currency: 'KRW',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
}

// 보고서 데이터 업데이트
function updateReportData(data) {
    document.getElementById('start-year').textContent = data.startYear;
    document.getElementById('investment-period').textContent = data.period + '년';
    document.getElementById('target-return').textContent = data.targetReturn + '%';
    document.getElementById('projected-assets').textContent = formatCurrency(data.projectedAssets);
    
    // 현재 날짜 업데이트
    const today = new Date();
    document.getElementById('report-date').textContent = 
        `${today.getFullYear()}년 ${today.getMonth() + 1}월 ${today.getDate()}일 작성`;
}

// 입력값 변경 시 실시간 계산
document.addEventListener('DOMContentLoaded', function() {
    const inputs = ['initial-amount', 'monthly-investment', 'period', 'interest-rate'];
    
    inputs.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.addEventListener('input', function() {
                // 디바운싱을 위한 타이머
                clearTimeout(window.calcTimer);
                window.calcTimer = setTimeout(calculateCompoundInterest, 500);
            });
        }
    });

    // 초기 계산 실행
    calculateCompoundInterest();
});