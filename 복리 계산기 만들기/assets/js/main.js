// 메인 애플리케이션 스크립트
document.addEventListener('DOMContentLoaded', function() {
    // 네비게이션 기능
    initNavigation();
    
    // 초기 데이터 로드
    initializeData();
    
    // 반응형 처리
    handleResponsive();
});

// 네비게이션 초기화
function initNavigation() {
    const navButtons = document.querySelectorAll('.nav-btn');
    const sections = document.querySelectorAll('.section');
    
    navButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetSection = this.getAttribute('data-section');
            
            // 모든 버튼과 섹션에서 active 클래스 제거
            navButtons.forEach(btn => btn.classList.remove('active'));
            sections.forEach(section => section.classList.remove('active'));
            
            // 클릭된 버튼과 해당 섹션에 active 클래스 추가
            this.classList.add('active');
            document.getElementById(targetSection).classList.add('active');
            
            // 특정 섹션 진입 시 추가 처리
            handleSectionChange(targetSection);
        });
    });
}

// 섹션 변경 시 처리
function handleSectionChange(sectionName) {
    switch(sectionName) {
        case 'calculator':
            // 계산기 섹션: 자동 계산 실행
            setTimeout(() => {
                if (typeof calculateCompoundInterest === 'function') {
                    calculateCompoundInterest();
                }
            }, 100);
            break;
            
        case 'planner':
            // 플래너 섹션: 타임라인 업데이트
            setTimeout(() => {
                if (typeof renderTimeline === 'function') {
                    renderTimeline();
                }
            }, 100);
            break;
            
        case 'report':
            // 보고서 섹션: 데이터 업데이트
            updateReportPreview();
            break;
    }
}

// 초기 데이터 설정
function initializeData() {
    // 현재 날짜 설정
    const today = new Date();
    document.getElementById('report-date').textContent = 
        `${today.getFullYear()}년 ${today.getMonth() + 1}월 ${today.getDate()}일 작성`;
    
    // 기본값으로 초기 계산 실행
    if (typeof calculateCompoundInterest === 'function') {
        calculateCompoundInterest();
    }
    
    // 로컬 스토리지에서 데이터 복원
    loadFromLocalStorage();
}

// 보고서 미리보기 업데이트
function updateReportPreview() {
    // 현재 입력된 데이터로 보고서 미리보기 업데이트
    const initialAmount = parseFloat(document.getElementById('initial-amount').value) || 0;
    const period = parseFloat(document.getElementById('period').value) || 0;
    const interestRate = parseFloat(document.getElementById('interest-rate').value) || 0;
    
    // 최종 자산 계산
    const monthlyInvestment = parseFloat(document.getElementById('monthly-investment').value) || 0;
    const monthlyRate = interestRate / 100 / 12;
    const totalMonths = period * 12;
    
    let finalAmount = initialAmount * Math.pow(1 + monthlyRate, totalMonths);
    if (monthlyInvestment > 0) {
        finalAmount += monthlyInvestment * 
            (Math.pow(1 + monthlyRate, totalMonths) - 1) / monthlyRate;
    }
    
    // 보고서 요약 정보 업데이트
    document.getElementById('start-year').textContent = new Date().getFullYear();
    document.getElementById('investment-period').textContent = period + '년';
    document.getElementById('target-return').textContent = interestRate + '%';
    document.getElementById('projected-assets').textContent = formatCurrency(finalAmount);
}

// 반응형 처리
function handleResponsive() {
    const handleResize = () => {
        const width = window.innerWidth;
        
        // 모바일에서 네비게이션 스타일 조정
        const nav = document.querySelector('.nav');
        if (width <= 768) {
            nav.style.flexWrap = 'wrap';
        } else {
            nav.style.flexWrap = 'nowrap';
        }
        
        // 차트 크기 조정
        if (window.compoundChart && typeof window.compoundChart.resize === 'function') {
            window.compoundChart.resize();
        }
    };
    
    window.addEventListener('resize', handleResize);
    handleResize(); // 초기 실행
}

// 로컬 스토리지 저장
function saveToLocalStorage() {
    const data = {
        initialAmount: document.getElementById('initial-amount').value,
        monthlyInvestment: document.getElementById('monthly-investment').value,
        period: document.getElementById('period').value,
        interestRate: document.getElementById('interest-rate').value,
        lifeEvents: typeof lifeEvents !== 'undefined' ? lifeEvents : [],
        lastSaved: Date.now()
    };
    
    try {
        localStorage.setItem('financialPlannerData', JSON.stringify(data));
    } catch (error) {
        console.warn('로컬 스토리지 저장 실패:', error);
    }
}

// 로컬 스토리지 로드
function loadFromLocalStorage() {
    try {
        const saved = localStorage.getItem('financialPlannerData');
        if (saved) {
            const data = JSON.parse(saved);
            
            // 입력 필드 복원
            if (data.initialAmount) document.getElementById('initial-amount').value = data.initialAmount;
            if (data.monthlyInvestment) document.getElementById('monthly-investment').value = data.monthlyInvestment;
            if (data.period) document.getElementById('period').value = data.period;
            if (data.interestRate) document.getElementById('interest-rate').value = data.interestRate;
            
            // 라이프 이벤트 복원
            if (data.lifeEvents && typeof lifeEvents !== 'undefined') {
                lifeEvents.length = 0; // 기존 배열 비우기
                lifeEvents.push(...data.lifeEvents);
                
                // UI 업데이트
                if (typeof renderLifeEvents === 'function') {
                    renderLifeEvents();
                }
                if (typeof renderTimeline === 'function') {
                    renderTimeline();
                }
            }
        }
    } catch (error) {
        console.warn('로컬 스토리지 로드 실패:', error);
    }
}

// 데이터 자동 저장 (입력값 변경 시)
document.addEventListener('DOMContentLoaded', function() {
    const inputs = ['initial-amount', 'monthly-investment', 'period', 'interest-rate'];
    
    inputs.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.addEventListener('change', saveToLocalStorage);
        }
    });
});

// 페이지 언로드 시 데이터 저장
window.addEventListener('beforeunload', function() {
    saveToLocalStorage();
});

// 키보드 단축키
document.addEventListener('keydown', function(e) {
    // Ctrl+1,2,3으로 섹션 전환
    if (e.ctrlKey) {
        const navButtons = document.querySelectorAll('.nav-btn');
        switch(e.key) {
            case '1':
                e.preventDefault();
                if (navButtons[0]) navButtons[0].click();
                break;
            case '2':
                e.preventDefault();
                if (navButtons[1]) navButtons[1].click();
                break;
            case '3':
                e.preventDefault();
                if (navButtons[2]) navButtons[2].click();
                break;
        }
    }
    
    // Ctrl+P로 PDF 생성
    if (e.ctrlKey && e.key === 'p') {
        e.preventDefault();
        if (typeof generatePDF === 'function') {
            generatePDF();
        }
    }
});

// 도움말 토글
function toggleHelp() {
    const helpModal = document.getElementById('help-modal');
    if (helpModal) {
        helpModal.style.display = helpModal.style.display === 'block' ? 'none' : 'block';
    }
}

// 테마 전환 (다크/라이트 모드)
function toggleTheme() {
    const body = document.body;
    const isDark = body.classList.contains('dark-theme');
    
    if (isDark) {
        body.classList.remove('dark-theme');
        localStorage.setItem('theme', 'light');
    } else {
        body.classList.add('dark-theme');
        localStorage.setItem('theme', 'dark');
    }
}

// 저장된 테마 로드
document.addEventListener('DOMContentLoaded', function() {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-theme');
    }
});

// 인쇄 기능
function printPage() {
    window.print();
}

// 데이터 내보내기/가져오기
function exportData() {
    const data = {
        initialAmount: document.getElementById('initial-amount').value,
        monthlyInvestment: document.getElementById('monthly-investment').value,
        period: document.getElementById('period').value,
        interestRate: document.getElementById('interest-rate').value,
        lifeEvents: typeof lifeEvents !== 'undefined' ? lifeEvents : [],
        exportDate: new Date().toISOString()
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `financial_plan_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function importData() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = function(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                try {
                    const data = JSON.parse(e.target.result);
                    
                    // 데이터 복원
                    if (data.initialAmount) document.getElementById('initial-amount').value = data.initialAmount;
                    if (data.monthlyInvestment) document.getElementById('monthly-investment').value = data.monthlyInvestment;
                    if (data.period) document.getElementById('period').value = data.period;
                    if (data.interestRate) document.getElementById('interest-rate').value = data.interestRate;
                    
                    if (data.lifeEvents && typeof lifeEvents !== 'undefined') {
                        lifeEvents.length = 0;
                        lifeEvents.push(...data.lifeEvents);
                        if (typeof renderLifeEvents === 'function') renderLifeEvents();
                        if (typeof renderTimeline === 'function') renderTimeline();
                    }
                    
                    // 계산 업데이트
                    if (typeof calculateCompoundInterest === 'function') {
                        calculateCompoundInterest();
                    }
                    
                    alert('데이터를 성공적으로 가져왔습니다.');
                } catch (error) {
                    alert('파일 형식이 올바르지 않습니다.');
                }
            };
            reader.readAsText(file);
        }
    };
    input.click();
}

// 전역 유틸리티 함수들
window.utils = {
    formatCurrency: formatCurrency,
    saveToLocalStorage: saveToLocalStorage,
    loadFromLocalStorage: loadFromLocalStorage,
    exportData: exportData,
    importData: importData,
    toggleTheme: toggleTheme,
    printPage: printPage
};

console.log('🎉 나의 금융 연대기가 성공적으로 로드되었습니다!');
console.log('💡 키보드 단축키: Ctrl+1,2,3 (섹션 전환), Ctrl+P (PDF 생성)');