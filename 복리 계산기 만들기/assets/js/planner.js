// 라이프 플래너 데이터 저장소
let lifeEvents = [];
let currentYear = new Date().getFullYear();

// 인생 이벤트 추가
function addLifeEvent() {
    const name = document.getElementById('event-name').value.trim();
    const year = parseInt(document.getElementById('event-year').value);
    const amount = parseFloat(document.getElementById('event-amount').value);

    if (!name || !year || !amount) {
        alert('모든 정보를 입력해주세요.');
        return;
    }

    if (year < currentYear) {
        alert('미래 년도를 입력해주세요.');
        return;
    }

    const event = {
        id: Date.now(),
        name: name,
        year: year,
        amount: amount,
        yearsFromNow: year - currentYear
    };

    lifeEvents.push(event);
    lifeEvents.sort((a, b) => a.year - b.year);

    // 입력 필드 초기화
    document.getElementById('event-name').value = '';
    document.getElementById('event-year').value = '';
    document.getElementById('event-amount').value = '';

    // UI 업데이트
    renderLifeEvents();
    renderTimeline();
}

// 인생 이벤트 삭제
function deleteLifeEvent(eventId) {
    lifeEvents = lifeEvents.filter(event => event.id !== eventId);
    renderLifeEvents();
    renderTimeline();
}

// 인생 이벤트 목록 렌더링
function renderLifeEvents() {
    const container = document.getElementById('events-list');
    
    if (lifeEvents.length === 0) {
        container.innerHTML = `
            <div style="text-align: center; color: #888; padding: 2rem;">
                <i class="fas fa-calendar-plus" style="font-size: 3rem; margin-bottom: 1rem;"></i>
                <p>아직 추가된 이벤트가 없습니다.<br>인생의 중요한 순간들을 추가해보세요!</p>
            </div>
        `;
        return;
    }

    container.innerHTML = lifeEvents.map(event => `
        <div class="event-item">
            <div class="event-info">
                <div class="event-name">${event.name}</div>
                <div class="event-details">
                    ${event.year}년 (${event.yearsFromNow}년 후) • ${formatCurrency(event.amount)}
                </div>
            </div>
            <button class="delete-btn" onclick="deleteLifeEvent(${event.id})">
                <i class="fas fa-trash"></i>
            </button>
        </div>
    `).join('');
}

// 타임라인 렌더링
function renderTimeline() {
    const container = document.getElementById('timeline');
    
    if (lifeEvents.length === 0) {
        container.innerHTML = `
            <div style="text-align: center; color: #888; padding: 2rem;">
                <i class="fas fa-timeline" style="font-size: 3rem; margin-bottom: 1rem;"></i>
                <p>이벤트를 추가하면 타임라인이 표시됩니다.</p>
            </div>
        `;
        return;
    }

    // 현재 투자 정보 가져오기
    const initialAmount = parseFloat(document.getElementById('initial-amount').value) || 0;
    const monthlyInvestment = parseFloat(document.getElementById('monthly-investment').value) || 0;
    const interestRate = parseFloat(document.getElementById('interest-rate').value) || 7;
    
    container.innerHTML = lifeEvents.map(event => {
        // 해당 년도까지의 예상 자산 계산
        const yearsToEvent = event.yearsFromNow;
        const projectedAssets = calculateAssetsAtYear(
            initialAmount, 
            monthlyInvestment, 
            interestRate, 
            yearsToEvent
        );
        
        const canAfford = projectedAssets >= event.amount;
        const shortage = event.amount - projectedAssets;
        
        return `
            <div class="timeline-item ${canAfford ? 'affordable' : 'shortage'}">
                <div class="timeline-year">${event.year}년</div>
                <div class="timeline-event">${event.name}</div>
                <div class="timeline-amount">필요 금액: ${formatCurrency(event.amount)}</div>
                <div class="timeline-projection">
                    예상 자산: ${formatCurrency(projectedAssets)}
                    ${canAfford 
                        ? `<span style="color: #4CAF50; margin-left: 10px;"><i class="fas fa-check-circle"></i> 달성 가능</span>`
                        : `<span style="color: #ff4757; margin-left: 10px;"><i class="fas fa-exclamation-circle"></i> ${formatCurrency(shortage)} 부족</span>`
                    }
                </div>
            </div>
        `;
    }).join('');
}

// 특정 년도의 예상 자산 계산
function calculateAssetsAtYear(initial, monthly, rate, years) {
    if (years <= 0) return initial;
    
    const monthlyRate = rate / 100 / 12;
    const totalMonths = years * 12;
    
    // 초기 투자액의 복리 계산
    const initialFutureValue = initial * Math.pow(1 + monthlyRate, totalMonths);
    
    // 월 투자액의 복리 계산
    let monthlyFutureValue = 0;
    if (monthly > 0) {
        monthlyFutureValue = monthly * 
            (Math.pow(1 + monthlyRate, totalMonths) - 1) / monthlyRate;
    }
    
    return initialFutureValue + monthlyFutureValue;
}

// 재무 목표 분석
function analyzeFinancialGoals() {
    const totalGoals = lifeEvents.reduce((sum, event) => sum + event.amount, 0);
    const currentInvestment = parseFloat(document.getElementById('initial-amount').value) || 0;
    const monthlyInvestment = parseFloat(document.getElementById('monthly-investment').value) || 0;
    const interestRate = parseFloat(document.getElementById('interest-rate').value) || 7;
    
    // 최장기 목표까지의 예상 자산
    const maxYear = Math.max(...lifeEvents.map(e => e.yearsFromNow));
    const projectedTotalAssets = calculateAssetsAtYear(
        currentInvestment, 
        monthlyInvestment, 
        interestRate, 
        maxYear
    );
    
    return {
        totalGoals,
        projectedTotalAssets,
        achievable: projectedTotalAssets >= totalGoals,
        shortfall: Math.max(0, totalGoals - projectedTotalAssets)
    };
}

// 추천 투자 전략 계산
function calculateRecommendedStrategy() {
    if (lifeEvents.length === 0) return null;
    
    const analysis = analyzeFinancialGoals();
    
    if (!analysis.achievable) {
        // 부족한 경우 필요한 월 투자액 계산
        const currentInitial = parseFloat(document.getElementById('initial-amount').value) || 0;
        const currentRate = parseFloat(document.getElementById('interest-rate').value) || 7;
        const maxYear = Math.max(...lifeEvents.map(e => e.yearsFromNow));
        
        // 목표 달성을 위한 월 투자액 역계산
        const monthlyRate = currentRate / 100 / 12;
        const totalMonths = maxYear * 12;
        const targetAmount = analysis.totalGoals;
        
        const initialFutureValue = currentInitial * Math.pow(1 + monthlyRate, totalMonths);
        const requiredFromMonthly = targetAmount - initialFutureValue;
        
        if (requiredFromMonthly > 0) {
            const requiredMonthlyInvestment = requiredFromMonthly * monthlyRate / 
                (Math.pow(1 + monthlyRate, totalMonths) - 1);
            
            return {
                type: 'increase_monthly',
                recommendedAmount: Math.ceil(requiredMonthlyInvestment / 10000) * 10000,
                message: `목표 달성을 위해 월 투자액을 ${formatCurrency(Math.ceil(requiredMonthlyInvestment / 10000) * 10000)}로 늘려보세요.`
            };
        }
    }
    
    return {
        type: 'achievable',
        message: '현재 투자 계획으로 모든 목표를 달성할 수 있습니다!'
    };
}

// 샘플 이벤트 추가 (초기 데모용)
function addSampleEvents() {
    const samples = [
        { name: '결혼', year: currentYear + 3, amount: 30000000 },
        { name: '내집마련', year: currentYear + 7, amount: 200000000 },
        { name: '자녀 대학등록금', year: currentYear + 20, amount: 100000000 },
        { name: '은퇴자금', year: currentYear + 30, amount: 1000000000 }
    ];
    
    lifeEvents = [...samples.map(s => ({
        ...s,
        id: Date.now() + Math.random(),
        yearsFromNow: s.year - currentYear
    }))];
    
    renderLifeEvents();
    renderTimeline();
}

// 이벤트 리스너 설정
document.addEventListener('DOMContentLoaded', function() {
    // 엔터키로 이벤트 추가
    ['event-name', 'event-year', 'event-amount'].forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    addLifeEvent();
                }
            });
        }
    });
    
    // 초기 렌더링
    renderLifeEvents();
    renderTimeline();
    
    // 샘플 이벤트 버튼 추가 (개발용)
    if (document.querySelector('.life-events h3')) {
        const sampleBtn = document.createElement('button');
        sampleBtn.innerHTML = '<i class="fas fa-magic"></i> 샘플 추가';
        sampleBtn.className = 'sample-btn';
        sampleBtn.style.cssText = `
            margin-left: 10px; 
            padding: 5px 10px; 
            font-size: 0.8rem; 
            background: #f0f0f0; 
            border: none; 
            border-radius: 5px; 
            cursor: pointer;
        `;
        sampleBtn.onclick = addSampleEvents;
        document.querySelector('.life-events h3').appendChild(sampleBtn);
    }
});

// 투자 설정 변경 시 타임라인 업데이트
document.addEventListener('DOMContentLoaded', function() {
    const inputs = ['initial-amount', 'monthly-investment', 'interest-rate'];
    
    inputs.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.addEventListener('input', function() {
                clearTimeout(window.timelineTimer);
                window.timelineTimer = setTimeout(renderTimeline, 300);
            });
        }
    });
});