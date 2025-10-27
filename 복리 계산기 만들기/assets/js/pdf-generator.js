// PDF 생성 함수 (한글 지원 개선)
async function generatePDF() {
    try {
        // 로딩 상태 표시
        const btn = document.querySelector('.generate-pdf-btn');
        const originalText = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 생성 중...';
        btn.disabled = true;

        // 대안: HTML을 이미지로 변환 후 PDF에 삽입하는 방식
        await generatePDFWithHTML2Canvas();
        
        // 성공 메시지
        showNotification('PDF가 성공적으로 생성되었습니다!', 'success');
        
    } catch (error) {
        console.error('PDF 생성 오류:', error);
        
        // 폴백: 기본 텍스트 PDF 생성
        try {
            await generateSimplePDF();
            showNotification('간단한 형태의 PDF가 생성되었습니다.', 'success');
        } catch (fallbackError) {
            showNotification('PDF 생성 중 오류가 발생했습니다.', 'error');
        }
    } finally {
        // 버튼 상태 복원
        const btn = document.querySelector('.generate-pdf-btn');
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

// HTML2Canvas를 이용한 PDF 생성 (한글 완벽 지원)
async function generatePDFWithHTML2Canvas() {
    const { jsPDF } = window.jspdf;
    const pdf = new jsPDF('p', 'mm', 'a4');
    
    // 보고서 데이터 수집
    const reportData = collectReportData();
    
    // 1페이지: 복리 투자 결과 + 그래프
    await generatePage1WithChart(pdf, reportData);
    
    // 2페이지: 인생 재무 계획
    if (reportData.lifeEvents.length > 0) {
        pdf.addPage();
        await generatePage2LifePlanning(pdf, reportData);
    }
    
    // 3페이지: 투자 성공 원칙
    pdf.addPage();
    await generatePage3Principles(pdf, reportData);
    
    // PDF 다운로드
    const fileName = `나의_금융_연대기_${new Date().toISOString().split('T')[0]}.pdf`;
    pdf.save(fileName);
}

// 1페이지: 복리 투자 결과 + 그래프
async function generatePage1WithChart(pdf, data) {
    // 제목과 기본 정보 HTML 생성
    const page1Element = createPage1HTML(data);
    document.body.appendChild(page1Element);
    
    try {
        // PDF용 차트 생성
        await createPDFChart(data);
        
        // 잠시 대기 (차트 렌더링 완료)
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // HTML을 캔버스로 변환
        const canvas = await html2canvas(page1Element, {
            scale: 2,
            useCORS: true,
            allowTaint: true,
            backgroundColor: '#ffffff',
            width: 794,
            height: 1123 // A4 비율
        });
        
        const imgData = canvas.toDataURL('image/png');
        const imgWidth = 210;
        const imgHeight = 297; // A4 높이
        
        // PDF에 이미지 추가
        pdf.addImage(imgData, 'PNG', 0, 0, imgWidth, imgHeight);
        
    } finally {
        // 임시 엘리먼트 제거
        document.body.removeChild(page1Element);
    }
}

// PDF용 차트 생성
async function createPDFChart(data) {
    const canvas = document.getElementById('pdf-chart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // 연도별 데이터 계산
    const labels = [];
    const principalData = [];
    const totalData = [];
    
    const monthlyRate = data.investment.interestRate / 100 / 12;
    const maxYears = Math.min(data.investment.period, 20); // 최대 20년까지 표시
    
    for (let year = 0; year <= maxYears; year += 2) {
        labels.push(year + '년');
        
        const months = year * 12;
        const principalAmount = data.investment.initialAmount + (data.investment.monthlyInvestment * months);
        
        let totalAmount = data.investment.initialAmount * Math.pow(1 + monthlyRate, months);
        if (data.investment.monthlyInvestment > 0 && months > 0) {
            totalAmount += data.investment.monthlyInvestment * (Math.pow(1 + monthlyRate, months) - 1) / monthlyRate;
        }
        
        principalData.push(principalAmount);
        totalData.push(totalAmount);
    }
    
    // 차트 생성
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: '투자원금',
                data: principalData,
                borderColor: '#ff6b6b',
                backgroundColor: 'rgba(255, 107, 107, 0.1)',
                fill: true,
                tension: 0.4,
                borderWidth: 2
            }, {
                label: '복리수익 포함',
                data: totalData,
                borderColor: '#4ecdc4',
                backgroundColor: 'rgba(78, 205, 196, 0.1)',
                fill: true,
                tension: 0.4,
                borderWidth: 2
            }]
        },
        options: {
            responsive: false,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        font: {
                            size: 11,
                            family: 'Noto Sans KR'
                        },
                        padding: 10
                    }
                },
                title: {
                    display: false
                }
            },
            scales: {
                x: {
                    grid: {
                        color: '#f0f0f0'
                    },
                    ticks: {
                        font: {
                            size: 10,
                            family: 'Noto Sans KR'
                        }
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        color: '#f0f0f0'
                    },
                    ticks: {
                        font: {
                            size: 10,
                            family: 'Noto Sans KR'
                        },
                        callback: function(value) {
                            if (value >= 100000000) {
                                return (value / 100000000).toFixed(0) + '억';
                            } else if (value >= 10000) {
                                return (value / 10000).toFixed(0) + '만';
                            }
                            return value.toLocaleString();
                        }
                    }
                }
            },
            elements: {
                point: {
                    radius: 3,
                    hoverRadius: 5
                }
            }
        }
    });
}

// 2페이지: 인생 재무 계획
async function generatePage2LifePlanning(pdf, data) {
    const page2Element = createPage2HTML(data);
    document.body.appendChild(page2Element);
    
    try {
        const canvas = await html2canvas(page2Element, {
            scale: 2,
            useCORS: true,
            allowTaint: true,
            backgroundColor: '#ffffff',
            width: 794,
            height: 1123
        });
        
        const imgData = canvas.toDataURL('image/png');
        const imgWidth = 210;
        const imgHeight = 297;
        
        pdf.addImage(imgData, 'PNG', 0, 0, imgWidth, imgHeight);
        
    } finally {
        document.body.removeChild(page2Element);
    }
}

// 3페이지: 투자 성공 원칙
async function generatePage3Principles(pdf, data) {
    const page3Element = createPage3HTML(data);
    document.body.appendChild(page3Element);
    
    try {
        const canvas = await html2canvas(page3Element, {
            scale: 2,
            useCORS: true,
            allowTaint: true,
            backgroundColor: '#ffffff',
            width: 794,
            height: 1123
        });
        
        const imgData = canvas.toDataURL('image/png');
        const imgWidth = 210;
        const imgHeight = 297;
        
        pdf.addImage(imgData, 'PNG', 0, 0, imgWidth, imgHeight);
        
    } finally {
        document.body.removeChild(page3Element);
    }
}

// 1페이지 HTML 생성 (제목 + 복리 결과 + 그래프)
function createPage1HTML(data) {
    const pageDiv = document.createElement('div');
    pageDiv.style.cssText = `
        width: 794px;
        height: 1123px;
        background: white;
        padding: 40px;
        font-family: 'Noto Sans KR', Arial, sans-serif;
        position: absolute;
        left: -9999px;
        top: 0;
        color: #333;
        display: flex;
        flex-direction: column;
    `;
    
    pageDiv.innerHTML = `
        <!-- 제목 영역 -->
        <div style="text-align: center; margin-bottom: 40px;">
            <h1 style="font-size: 36px; color: #667eea; margin-bottom: 15px;">나의 금융 연대기</h1>
            <h2 style="font-size: 20px; color: #666; margin-bottom: 20px;">개인 재무 분석 보고서</h2>
            <p style="font-size: 14px; color: #888;">작성일: ${data.personal.reportDate}</p>
        </div>
        
        <!-- 투자 계획 요약 -->
        <div style="margin-bottom: 30px; padding: 20px; background: #f8f9ff; border-radius: 10px; border-left: 4px solid #667eea;">
            <h3 style="color: #667eea; margin-bottom: 15px; font-size: 18px;">📋 투자 계획 요약</h3>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; font-size: 13px;">
                <div>
                    <p style="margin: 3px 0;"><strong>투자 시작:</strong> ${data.personal.currentYear}년</p>
                    <p style="margin: 3px 0;"><strong>투자 기간:</strong> ${data.investment.period}년</p>
                    <p style="margin: 3px 0;"><strong>목표 수익률:</strong> ${data.investment.interestRate}%</p>
                </div>
                <div>
                    <p style="margin: 3px 0;"><strong>초기 투자액:</strong> ${formatCurrencyKRW(data.investment.initialAmount)}</p>
                    <p style="margin: 3px 0;"><strong>월 투자액:</strong> ${formatCurrencyKRW(data.investment.monthlyInvestment)}</p>
                    <p style="margin: 3px 0;"><strong>예상 최종 자산:</strong> ${formatCurrencyKRW(data.investment.finalAmount)}</p>
                </div>
            </div>
        </div>
        
        <!-- 복리 투자 결과와 그래프 영역 -->
        <div style="display: flex; gap: 20px; flex: 1;">
            <!-- 복리 결과 -->
            <div style="flex: 1;">
                <h3 style="color: #667eea; margin-bottom: 15px; font-size: 18px;">💰 복리 투자 결과</h3>
                <div style="background: white; padding: 15px; border: 2px solid #e0e0e0; border-radius: 10px;">
                    <div style="margin-bottom: 10px; padding: 8px; background: #f9f9f9; border-radius: 5px;">
                        <strong>총 투자원금:</strong> ${formatCurrencyKRW(data.investment.totalInvestment)}
                    </div>
                    <div style="margin-bottom: 10px; padding: 8px; background: #e8f5e8; border-radius: 5px;">
                        <strong>복리 수익:</strong> <span style="color: #4CAF50; font-weight: bold;">${formatCurrencyKRW(data.investment.totalProfit)}</span>
                    </div>
                    <div style="margin-bottom: 15px; padding: 10px; background: #667eea; color: white; border-radius: 5px; text-align: center;">
                        <strong style="font-size: 16px;">최종 자산: ${formatCurrencyKRW(data.investment.finalAmount)}</strong>
                    </div>
                    <div style="font-size: 12px; color: #666; padding: 8px; background: #fff3cd; border-radius: 5px;">
                        <strong>💡 72의 법칙:</strong><br>
                        연 ${data.investment.interestRate}% 수익률로 투자하면 약 ${(72/data.investment.interestRate).toFixed(1)}년 후에 원금이 2배가 됩니다.
                    </div>
                </div>
            </div>
            
            <!-- 그래프 영역 -->
            <div style="flex: 1;">
                <h3 style="color: #667eea; margin-bottom: 15px; font-size: 18px;">📈 자산 증가 그래프</h3>
                <div id="pdf-chart-container" style="width: 100%; height: 300px; border: 2px solid #e0e0e0; border-radius: 10px; padding: 10px; background: white;">
                    <canvas id="pdf-chart" width="300" height="280"></canvas>
                </div>
            </div>
        </div>
        
        <!-- 하단 메시지 -->
        <div style="text-align: center; color: #888; font-size: 11px; border-top: 1px solid #eee; padding-top: 15px; margin-top: 20px;">
            <p>© 2025 나의 금융 연대기 - 당신의 재무 자유를 응원합니다</p>
        </div>
    `;
    
    return pageDiv;
}

// 2페이지 HTML 생성 (인생 재무 계획)
function createPage2HTML(data) {
    const pageDiv = document.createElement('div');
    pageDiv.style.cssText = `
        width: 794px;
        height: 1123px;
        background: white;
        padding: 40px;
        font-family: 'Noto Sans KR', Arial, sans-serif;
        position: absolute;
        left: -9999px;
        top: 0;
        color: #333;
    `;
    
    const eventsHtml = data.lifeEvents.length > 0 ? data.lifeEvents.map((event, index) => {
        const projectedAssets = calculateAssetsAtYear(
            data.investment.initialAmount,
            data.investment.monthlyInvestment,
            data.investment.interestRate,
            event.yearsFromNow
        );
        const canAfford = projectedAssets >= event.amount;
        return `
            <div style="background: ${canAfford ? '#e8f5e8' : '#ffeaea'}; padding: 15px; margin-bottom: 15px; border-radius: 8px; border-left: 4px solid ${canAfford ? '#4CAF50' : '#f44336'};">
                <h4 style="margin: 0 0 8px 0; color: #333; font-size: 16px;">${index + 1}. ${event.name} (${event.year}년)</h4>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 13px;">
                    <div>
                        <p style="margin: 3px 0;"><strong>필요 금액:</strong> ${formatCurrencyKRW(event.amount)}</p>
                        <p style="margin: 3px 0;"><strong>예상 자산:</strong> ${formatCurrencyKRW(projectedAssets)}</p>
                    </div>
                    <div>
                        <p style="margin: 3px 0; color: ${canAfford ? '#4CAF50' : '#f44336'}; font-weight: bold;">
                            ${canAfford ? '✓ 달성 가능' : '✗ 자금 부족'}
                        </p>
                        ${!canAfford ? `<p style="margin: 3px 0; color: #f44336; font-size: 12px;">부족 금액: ${formatCurrencyKRW(event.amount - projectedAssets)}</p>` : ''}
                    </div>
                </div>
            </div>
        `;
    }).join('') : '<p style="text-align: center; color: #888; padding: 40px;">등록된 인생 이벤트가 없습니다.</p>';
    
    pageDiv.innerHTML = `
        <div style="text-align: center; margin-bottom: 40px;">
            <h1 style="font-size: 32px; color: #667eea; margin-bottom: 15px;">🗓️ 인생 재무 계획</h1>
            <p style="font-size: 16px; color: #666;">당신의 인생 목표와 재무 계획을 확인해보세요</p>
        </div>
        
        <div style="margin-bottom: 30px;">
            <h3 style="color: #667eea; margin-bottom: 20px; font-size: 20px;">등록된 인생 이벤트</h3>
            ${eventsHtml}
        </div>
        
        ${data.analysis ? `
        <div style="margin-bottom: 30px; padding: 20px; background: #f0f8ff; border-radius: 10px; border-left: 4px solid #667eea;">
            <h3 style="color: #667eea; margin-bottom: 15px; font-size: 18px;">📊 재무 목표 분석</h3>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                <div>
                    <p style="margin: 5px 0;"><strong>총 목표 금액:</strong> ${formatCurrencyKRW(data.analysis.totalGoals)}</p>
                    <p style="margin: 5px 0;"><strong>예상 총 자산:</strong> ${formatCurrencyKRW(data.analysis.projectedTotalAssets)}</p>
                </div>
                <div>
                    <p style="margin: 5px 0; font-weight: bold; color: ${data.analysis.achievable ? '#4CAF50' : '#f44336'};">
                        ${data.analysis.achievable ? '🎯 모든 목표 달성 가능!' : '⚠️ 추가 노력 필요'}
                    </p>
                    ${!data.analysis.achievable ? `<p style="margin: 5px 0; color: #f44336;">부족 금액: ${formatCurrencyKRW(data.analysis.shortfall)}</p>` : ''}
                </div>
            </div>
        </div>
        ` : ''}
        
        <div style="text-align: center; color: #888; font-size: 11px; border-top: 1px solid #eee; padding-top: 15px; position: absolute; bottom: 40px; left: 40px; right: 40px;">
            <p>인생의 소중한 순간들을 위한 체계적인 재무 계획이 성공의 열쇠입니다.</p>
        </div>
    `;
    
    return pageDiv;
}

// 3페이지 HTML 생성 (투자 성공 원칙)
function createPage3HTML(data) {
    const pageDiv = document.createElement('div');
    pageDiv.style.cssText = `
        width: 794px;
        height: 1123px;
        background: white;
        padding: 40px;
        font-family: 'Noto Sans KR', Arial, sans-serif;
        position: absolute;
        left: -9999px;
        top: 0;
        color: #333;
    `;
    
    pageDiv.innerHTML = `
        <div style="text-align: center; margin-bottom: 40px;">
            <h1 style="font-size: 32px; color: #667eea; margin-bottom: 15px;">🎯 투자 성공 전략</h1>
            <p style="font-size: 16px; color: #666;">재무 자유를 위한 검증된 투자 원칙들</p>
        </div>
        
        <div style="margin-bottom: 40px;">
            <h3 style="color: #667eea; margin-bottom: 20px; font-size: 20px;">💡 성공적인 투자를 위한 5가지 원칙</h3>
            <div style="display: grid; gap: 15px;">
                <div style="background: #f8f9ff; padding: 15px; border-radius: 8px; border-left: 4px solid #667eea;">
                    <h4 style="color: #667eea; margin: 0 0 8px 0;">1. 장기 투자의 힘</h4>
                    <p style="margin: 0; font-size: 14px; line-height: 1.6;">시간이 길수록 복리 효과가 극대화됩니다. 단기 변동성에 흔들리지 말고 꾸준히 투자하세요.</p>
                </div>
                <div style="background: #f0f8ff; padding: 15px; border-radius: 8px; border-left: 4px solid #4ecdc4;">
                    <h4 style="color: #4ecdc4; margin: 0 0 8px 0;">2. 분산 투자로 리스크 관리</h4>
                    <p style="margin: 0; font-size: 14px; line-height: 1.6;">한 곳에 모든 돈을 투자하지 마세요. 여러 자산에 분산하여 위험을 줄이고 안정적인 수익을 추구하세요.</p>
                </div>
                <div style="background: #f0fff0; padding: 15px; border-radius: 8px; border-left: 4px solid #4CAF50;">
                    <h4 style="color: #4CAF50; margin: 0 0 8px 0;">3. 정기적인 적립식 투자</h4>
                    <p style="margin: 0; font-size: 14px; line-height: 1.6;">매월 일정 금액을 투자하여 시장 변동성을 평균화하고 감정적 투자를 피하세요.</p>
                </div>
                <div style="background: #fff8f0; padding: 15px; border-radius: 8px; border-left: 4px solid #ff9800;">
                    <h4 style="color: #ff9800; margin: 0 0 8px 0;">4. 명확한 목표 설정</h4>
                    <p style="margin: 0; font-size: 14px; line-height: 1.6;">구체적인 재무 목표를 설정하고 이를 달성하기 위한 계획을 세우세요. 목표가 있어야 동기부여가 됩니다.</p>
                </div>
                <div style="background: #f5f0ff; padding: 15px; border-radius: 8px; border-left: 4px solid #9c27b0;">
                    <h4 style="color: #9c27b0; margin: 0 0 8px 0;">5. 지속적인 학습과 점검</h4>
                    <p style="margin: 0; font-size: 14px; line-height: 1.6;">투자 지식을 계속 쌓고, 정기적으로 포트폴리오를 점검하여 필요시 조정하세요.</p>
                </div>
            </div>
        </div>
        
        <div style="margin-bottom: 30px;">
            <h3 style="color: #667eea; margin-bottom: 20px; font-size: 20px;">⚠️ 리스크 관리 방안</h3>
            <div style="background: #fff5f5; padding: 20px; border-radius: 10px; border-left: 4px solid #f44336;">
                <ul style="margin: 0; padding-left: 20px; line-height: 1.8; font-size: 14px;">
                    <li><strong>비상 자금 준비:</strong> 월 생활비의 3-6개월분을 따로 준비하세요</li>
                    <li><strong>보험 가입:</strong> 예상치 못한 위험에 대비한 보험에 가입하세요</li>
                    <li><strong>나이에 맞는 투자:</strong> 나이가 들수록 안전 자산 비중을 늘리세요</li>
                    <li><strong>정기적인 리밸런싱:</strong> 시장 상황에 따라 포트폴리오를 조정하세요</li>
                </ul>
            </div>
        </div>
        
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; text-align: center;">
            <h4 style="margin: 0 0 10px 0; font-size: 18px;">🚀 당신의 재무 자유를 응원합니다!</h4>
            <p style="margin: 0; font-size: 14px; opacity: 0.9;">작은 시작이 큰 부를 만듭니다. 오늘부터 시작하세요!</p>
        </div>
        
        <div style="text-align: center; color: #888; font-size: 10px; position: absolute; bottom: 20px; left: 40px; right: 40px;">
            <p>본 보고서는 참고용이며, 실제 투자 결정 시에는 전문가와 상담하시기 바랍니다.</p>
            <p>© 2025 나의 금융 연대기. All rights reserved.</p>
        </div>
    `;
    
    return pageDiv;
}

// 폴백: 간단한 PDF 생성 (ASCII 문자만 사용)
async function generateSimplePDF() {
    const { jsPDF } = window.jspdf;
    const pdf = new jsPDF('p', 'mm', 'a4');
    
    const data = collectReportData();
    
    // 제목 (영문으로)
    pdf.setFontSize(20);
    pdf.text('My Financial Chronicle', 105, 30, { align: 'center' });
    
    pdf.setFontSize(14);
    pdf.text('Personal Financial Analysis Report', 105, 45, { align: 'center' });
    
    // 날짜
    pdf.setFontSize(12);
    pdf.text(`Date: ${data.personal.reportDate}`, 105, 60, { align: 'center' });
    
    // 투자 정보 (숫자는 정상 표시)
    pdf.setFontSize(14);
    pdf.text('Investment Summary', 20, 85);
    
    pdf.setFontSize(12);
    const startY = 100;
    const lineHeight = 8;
    
    pdf.text(`Start Year: ${data.personal.currentYear}`, 25, startY);
    pdf.text(`Investment Period: ${data.investment.period} years`, 25, startY + lineHeight);
    pdf.text(`Target Return: ${data.investment.interestRate}%`, 25, startY + lineHeight * 2);
    pdf.text(`Initial Amount: ${formatNumber(data.investment.initialAmount)} won`, 25, startY + lineHeight * 3);
    pdf.text(`Monthly Investment: ${formatNumber(data.investment.monthlyInvestment)} won`, 25, startY + lineHeight * 4);
    pdf.text(`Projected Assets: ${formatNumber(data.investment.finalAmount)} won`, 25, startY + lineHeight * 5);
    
    // 복리 결과
    pdf.setFontSize(14);
    pdf.text('Compound Interest Results', 20, startY + lineHeight * 8);
    
    pdf.setFontSize(12);
    const resultY = startY + lineHeight * 9.5;
    pdf.text(`Total Investment: ${formatNumber(data.investment.totalInvestment)} won`, 25, resultY);
    pdf.text(`Compound Profit: ${formatNumber(data.investment.totalProfit)} won`, 25, resultY + lineHeight);
    pdf.text(`Final Amount: ${formatNumber(data.investment.finalAmount)} won`, 25, resultY + lineHeight * 2);
    
    const doubleTime = (72 / data.investment.interestRate).toFixed(1);
    pdf.text(`Rule of 72: Money doubles in ${doubleTime} years`, 25, resultY + lineHeight * 4);
    
    // 하단 메시지
    pdf.setFontSize(10);
    pdf.text('This report is for reference only.', 105, 250, { align: 'center' });
    pdf.text('Please consult with a financial advisor for investment decisions.', 105, 260, { align: 'center' });
    
    // PDF 다운로드
    const fileName = `Financial_Report_${new Date().toISOString().split('T')[0]}.pdf`;
    pdf.save(fileName);
}

// 숫자 포맷팅 (영문용) - 소숫점 제거
function formatNumber(num) {
    return new Intl.NumberFormat('en-US', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(Math.round(num));
}

// 보고서 데이터 수집
function collectReportData() {
    const initialAmount = parseFloat(document.getElementById('initial-amount').value) || 0;
    const monthlyInvestment = parseFloat(document.getElementById('monthly-investment').value) || 0;
    const period = parseFloat(document.getElementById('period').value) || 0;
    const interestRate = parseFloat(document.getElementById('interest-rate').value) || 0;
    
    // 복리 계산 결과
    const monthlyRate = interestRate / 100 / 12;
    const totalMonths = period * 12;
    const initialFutureValue = initialAmount * Math.pow(1 + monthlyRate, totalMonths);
    const monthlyFutureValue = monthlyInvestment > 0 ? 
        monthlyInvestment * (Math.pow(1 + monthlyRate, totalMonths) - 1) / monthlyRate : 0;
    const finalAmount = initialFutureValue + monthlyFutureValue;
    const totalInvestment = initialAmount + (monthlyInvestment * totalMonths);
    const totalProfit = finalAmount - totalInvestment;
    
    return {
        personal: {
            reportDate: new Date().toLocaleDateString('ko-KR'),
            currentYear: new Date().getFullYear()
        },
        investment: {
            initialAmount,
            monthlyInvestment,
            period,
            interestRate,
            totalInvestment,
            totalProfit,
            finalAmount
        },
        lifeEvents: [...lifeEvents],
        analysis: analyzeFinancialGoals(),
        recommendations: calculateRecommendedStrategy()
    };
}

// 표지 페이지 생성
function generateCoverPage(pdf, data) {
    // 제목
    pdf.setFontSize(24);
    pdf.setFont(undefined, 'bold');
    pdf.text('나의 금융 연대기', 105, 60, { align: 'center' });
    
    // 부제목
    pdf.setFontSize(16);
    pdf.setFont(undefined, 'normal');
    pdf.text('개인 재무 분석 보고서', 105, 75, { align: 'center' });
    
    // 날짜
    pdf.setFontSize(12);
    pdf.text(`작성일: ${data.personal.reportDate}`, 105, 90, { align: 'center' });
    
    // 구분선
    pdf.setLineWidth(0.5);
    pdf.line(40, 110, 170, 110);
    
    // 요약 정보
    pdf.setFontSize(14);
    pdf.setFont(undefined, 'bold');
    pdf.text('투자 계획 요약', 40, 130);
    
    pdf.setFontSize(12);
    pdf.setFont(undefined, 'normal');
    const summaryY = 145;
    const lineHeight = 8;
    
    pdf.text(`• 투자 시작 연도: ${data.personal.currentYear}년`, 50, summaryY);
    pdf.text(`• 투자 기간: ${data.investment.period}년`, 50, summaryY + lineHeight);
    pdf.text(`• 목표 수익률: ${data.investment.interestRate}%`, 50, summaryY + lineHeight * 2);
    pdf.text(`• 초기 투자액: ${formatCurrencyKRW(data.investment.initialAmount)}`, 50, summaryY + lineHeight * 3);
    pdf.text(`• 월 투자액: ${formatCurrencyKRW(data.investment.monthlyInvestment)}`, 50, summaryY + lineHeight * 4);
    pdf.text(`• 예상 최종 자산: ${formatCurrencyKRW(data.investment.finalAmount)}`, 50, summaryY + lineHeight * 5);
    
    // 하단 정보
    pdf.setFontSize(10);
    pdf.text('본 보고서는 입력하신 정보를 바탕으로 작성되었습니다.', 105, 250, { align: 'center' });
    pdf.text('실제 투자 결과는 시장 상황에 따라 달라질 수 있습니다.', 105, 260, { align: 'center' });
}

// 투자 계획 요약 페이지
function generateInvestmentSummaryPage(pdf, data) {
    pdf.setFontSize(18);
    pdf.setFont(undefined, 'bold');
    pdf.text('투자 계획 상세 분석', 40, 30);
    
    // 복리 효과 설명
    pdf.setFontSize(14);
    pdf.setFont(undefined, 'bold');
    pdf.text('1. 복리 투자 효과', 40, 50);
    
    pdf.setFontSize(12);
    pdf.setFont(undefined, 'normal');
    const y1 = 60;
    const lh = 7;
    
    pdf.text(`초기 투자금: ${formatCurrencyKRW(data.investment.initialAmount)}`, 45, y1);
    pdf.text(`월 적립금: ${formatCurrencyKRW(data.investment.monthlyInvestment)}`, 45, y1 + lh);
    pdf.text(`투자 기간: ${data.investment.period}년 (${data.investment.period * 12}개월)`, 45, y1 + lh * 2);
    pdf.text(`연 수익률: ${data.investment.interestRate}%`, 45, y1 + lh * 3);
    
    // 결과 요약
    pdf.setFontSize(14);
    pdf.setFont(undefined, 'bold');
    pdf.text('2. 투자 결과 예측', 40, y1 + lh * 6);
    
    pdf.setFontSize(12);
    pdf.setFont(undefined, 'normal');
    const y2 = y1 + lh * 7;
    
    pdf.text(`총 투자원금: ${formatCurrencyKRW(data.investment.totalInvestment)}`, 45, y2);
    pdf.text(`복리 수익: ${formatCurrencyKRW(data.investment.totalProfit)}`, 45, y2 + lh);
    pdf.text(`최종 자산: ${formatCurrencyKRW(data.investment.finalAmount)}`, 45, y2 + lh * 2);
    
    const profitRate = (data.investment.totalProfit / data.investment.totalInvestment * 100).toFixed(1);
    pdf.text(`수익률: ${profitRate}%`, 45, y2 + lh * 3);
    
    // 72의 법칙
    pdf.setFontSize(14);
    pdf.setFont(undefined, 'bold');
    pdf.text('3. 72의 법칙', 40, y2 + lh * 6);
    
    pdf.setFontSize(12);
    pdf.setFont(undefined, 'normal');
    const doubleTime = (72 / data.investment.interestRate).toFixed(1);
    pdf.text(`연 ${data.investment.interestRate}% 수익률로 투자하면`, 45, y2 + lh * 7.5);
    pdf.text(`약 ${doubleTime}년 후에 원금이 2배가 됩니다.`, 45, y2 + lh * 8.5);
    
    // 중요 포인트
    pdf.setFontSize(14);
    pdf.setFont(undefined, 'bold');
    pdf.text('4. 핵심 포인트', 40, y2 + lh * 11);
    
    pdf.setFontSize(12);
    pdf.setFont(undefined, 'normal');
    pdf.text('• 복리의 힘: 시간이 지날수록 수익이 기하급수적으로 증가', 45, y2 + lh * 12.5);
    pdf.text('• 꾸준한 투자: 매월 일정 금액 투자로 평균 매입 단가 효과', 45, y2 + lh * 13.5);
    pdf.text('• 장기 투자: 시간이 길수록 복리 효과 극대화', 45, y2 + lh * 14.5);
}

// 복리 계산 결과 페이지 (차트 포함)
async function generateCompoundResultsPage(pdf, data) {
    pdf.setFontSize(18);
    pdf.setFont(undefined, 'bold');
    pdf.text('복리 투자 시뮬레이션', 40, 30);
    
    // 연도별 자산 증가 테이블
    pdf.setFontSize(14);
    pdf.setFont(undefined, 'bold');
    pdf.text('연도별 자산 증가 현황', 40, 50);
    
    // 테이블 헤더
    pdf.setFontSize(10);
    pdf.setFont(undefined, 'bold');
    const tableStartY = 65;
    const colWidths = [25, 35, 35, 35, 35];
    const headers = ['연도', '누적 투자', '복리 수익', '총 자산', '수익률'];
    
    let x = 40;
    headers.forEach((header, i) => {
        pdf.rect(x, tableStartY, colWidths[i], 8);
        pdf.text(header, x + colWidths[i]/2, tableStartY + 5, { align: 'center' });
        x += colWidths[i];
    });
    
    // 테이블 데이터 (5년 간격)
    pdf.setFont(undefined, 'normal');
    let currentY = tableStartY + 8;
    
    for (let year = 0; year <= data.investment.period; year += 5) {
        if (year === 0) continue;
        
        const months = year * 12;
        const principalAmount = data.investment.initialAmount + (data.investment.monthlyInvestment * months);
        const monthlyRate = data.investment.interestRate / 100 / 12;
        
        let totalAmount = data.investment.initialAmount * Math.pow(1 + monthlyRate, months);
        if (data.investment.monthlyInvestment > 0) {
            totalAmount += data.investment.monthlyInvestment * 
                (Math.pow(1 + monthlyRate, months) - 1) / monthlyRate;
        }
        
        const profit = totalAmount - principalAmount;
        const profitRate = principalAmount > 0 ? (profit / principalAmount * 100).toFixed(1) : '0.0';
        
        const rowData = [
            `${year}년`,
            formatCurrencyKRWShort(principalAmount),
            formatCurrencyKRWShort(profit),
            formatCurrencyKRWShort(totalAmount),
            `${profitRate}%`
        ];
        
        x = 40;
        rowData.forEach((data, i) => {
            pdf.rect(x, currentY, colWidths[i], 8);
            pdf.text(data, x + colWidths[i]/2, currentY + 5, { align: 'center' });
            x += colWidths[i];
        });
        
        currentY += 8;
        if (currentY > 250) break; // 페이지 넘침 방지
    }
    
    // 차트 캡처 및 삽입 (간단한 텍스트 설명으로 대체)
    pdf.setFontSize(12);
    pdf.setFont(undefined, 'normal');
    const chartY = Math.min(currentY + 20, 200);
    pdf.text('※ 차트는 웹페이지에서 확인하실 수 있습니다.', 40, chartY);
    pdf.text('투자 기간이 길어질수록 복리 효과로 인해', 40, chartY + 10);
    pdf.text('자산 증가율이 가속화되는 것을 확인할 수 있습니다.', 40, chartY + 20);
}

// 라이프 플래닝 페이지
function generateLifePlanningPage(pdf, data) {
    pdf.setFontSize(18);
    pdf.setFont(undefined, 'bold');
    pdf.text('인생 재무 계획', 40, 30);
    
    if (data.lifeEvents.length === 0) {
        pdf.setFontSize(12);
        pdf.setFont(undefined, 'normal');
        pdf.text('등록된 인생 이벤트가 없습니다.', 40, 60);
        pdf.text('웹페이지에서 결혼, 내집마련, 자녀 교육비 등', 40, 75);
        pdf.text('인생의 중요한 이벤트들을 추가해보세요.', 40, 90);
        return;
    }
    
    pdf.setFontSize(14);
    pdf.setFont(undefined, 'bold');
    pdf.text('등록된 인생 이벤트', 40, 50);
    
    // 이벤트 목록
    pdf.setFontSize(12);
    pdf.setFont(undefined, 'normal');
    let currentY = 65;
    
    for (let index = 0; index < data.lifeEvents.length; index++) {
        if (currentY > 250) break; // 페이지 넘침 방지
        
        const event = data.lifeEvents[index];
        const projectedAssets = calculateAssetsAtYear(
            data.investment.initialAmount,
            data.investment.monthlyInvestment,
            data.investment.interestRate,
            event.yearsFromNow
        );
        
        const canAfford = projectedAssets >= event.amount;
        const statusText = canAfford ? '[달성 가능]' : '[자금 부족]';
        
        pdf.setFont(undefined, 'bold');
        pdf.text(`${index + 1}. ${event.name} (${event.year}년)`, 45, currentY);
        
        pdf.setFont(undefined, 'normal');
        pdf.text(`필요 금액: ${formatCurrencyKRW(event.amount)}`, 45, currentY + 7);
        pdf.text(`예상 자산: ${formatCurrencyKRW(projectedAssets)}`, 45, currentY + 14);
        pdf.text(`상태: ${statusText}`, 45, currentY + 21);
        
        if (!canAfford) {
            const shortage = event.amount - projectedAssets;
            pdf.text(`부족 금액: ${formatCurrencyKRW(shortage)}`, 45, currentY + 28);
            currentY += 35;
        } else {
            currentY += 28;
        }
        
        currentY += 10; // 이벤트 간 간격
    }
    
    // 분석 요약
    if (data.analysis) {
        pdf.setFontSize(14);
        pdf.setFont(undefined, 'bold');
        pdf.text('재무 목표 분석', 40, Math.min(currentY + 20, 220));
        
        pdf.setFontSize(12);
        pdf.setFont(undefined, 'normal');
        const analysisY = Math.min(currentY + 35, 235);
        pdf.text(`총 목표 금액: ${formatCurrencyKRW(data.analysis.totalGoals)}`, 45, analysisY);
        pdf.text(`예상 총 자산: ${formatCurrencyKRW(data.analysis.projectedTotalAssets)}`, 45, analysisY + 7);
        
        if (data.analysis.achievable) {
            pdf.text('현재 계획으로 모든 목표를 달성할 수 있습니다!', 45, analysisY + 14);
        } else {
            pdf.text(`목표 달성을 위해 ${formatCurrencyKRW(data.analysis.shortfall)} 추가 필요`, 45, analysisY + 14);
        }
    }
}

// 추천 전략 페이지
function generateRecommendationsPage(pdf, data) {
    pdf.setFontSize(18);
    pdf.setFont(undefined, 'bold');
    pdf.text('맞춤 투자 전략 제안', 40, 30);
    
    // 현재 투자 전략 평가
    pdf.setFontSize(14);
    pdf.setFont(undefined, 'bold');
    pdf.text('1. 현재 투자 계획 평가', 40, 50);
    
    pdf.setFontSize(12);
    pdf.setFont(undefined, 'normal');
    let currentY = 65;
    
    if (data.recommendations) {
        if (data.recommendations.type === 'achievable') {
            pdf.text('✓ 현재 투자 계획이 우수합니다.', 45, currentY);
            pdf.text('  모든 인생 목표를 달성할 수 있는 계획입니다.', 45, currentY + 7);
        } else if (data.recommendations.type === 'increase_monthly') {
            pdf.text('△ 월 투자액 증액이 필요합니다.', 45, currentY);
            pdf.text(`  권장 월 투자액: ${formatCurrencyKRW(data.recommendations.recommendedAmount)}`, 45, currentY + 7);
        }
    }
    
    // 일반적인 투자 원칙
    currentY += 30;
    pdf.setFontSize(14);
    pdf.setFont(undefined, 'bold');
    pdf.text('2. 성공적인 투자를 위한 원칙', 40, currentY);
    
    currentY += 15;
    pdf.setFontSize(12);
    pdf.setFont(undefined, 'normal');
    
    const principles = [
        '장기 투자: 시간이 길수록 복리 효과가 극대화됩니다',
        '분산 투자: 위험을 줄이고 안정적인 수익을 추구하세요',
        '꾸준한 적립: 시장 변동성을 평균화할 수 있습니다',
        '목표 기반 투자: 명확한 목표를 설정하고 계획을 세우세요',
        '정기적인 점검: 6개월마다 투자 계획을 검토하세요'
    ];
    
    principles.forEach((principle, index) => {
        pdf.text(`${index + 1}. ${principle}`, 45, currentY);
        currentY += 10;
    });
    
    // 리스크 관리
    currentY += 15;
    pdf.setFontSize(14);
    pdf.setFont(undefined, 'bold');
    pdf.text('3. 리스크 관리 방안', 40, currentY);
    
    currentY += 15;
    pdf.setFontSize(12);
    pdf.setFont(undefined, 'normal');
    
    const riskManagement = [
        '비상 자금: 월 생활비의 3-6개월분을 준비하세요',
        '보험 가입: 예상치 못한 위험에 대비하세요',
        '투자 비율 조절: 나이에 따라 안전 자산 비중을 늘리세요',
        '정기적인 리밸런싱: 시장 상황에 따라 포트폴리오를 조정하세요'
    ];
    
    riskManagement.forEach((item, index) => {
        pdf.text(`• ${item}`, 45, currentY);
        currentY += 10;
    });
    
    // 하단 메시지
    pdf.setFontSize(10);
    pdf.setFont(undefined, 'italic');
    pdf.text('본 보고서는 참고용이며, 실제 투자 결정 시에는 전문가와 상담하시기 바랍니다.', 105, 270, { align: 'center' });
}

// 통화 형식 변환 (PDF용) - 소숫점 제거
function formatCurrencyKRW(amount) {
    return new Intl.NumberFormat('ko-KR', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(Math.round(amount)) + '원';
}

function formatCurrencyKRWShort(amount) {
    const roundedAmount = Math.round(amount);
    if (roundedAmount >= 100000000) {
        return Math.round(roundedAmount / 100000000) + '억원';
    } else if (roundedAmount >= 10000) {
        return Math.round(roundedAmount / 10000) + '만원';
    } else {
        return formatCurrencyKRW(roundedAmount);
    }
}

// 알림 표시 함수
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        z-index: 1000;
        animation: slideIn 0.3s ease-out;
        max-width: 300px;
    `;
    
    if (type === 'success') {
        notification.style.background = '#4CAF50';
    } else if (type === 'error') {
        notification.style.background = '#f44336';
    } else {
        notification.style.background = '#2196F3';
    }
    
    notification.textContent = message;
    document.body.appendChild(notification);
    
    // 3초 후 제거
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// CSS 애니메이션 추가
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);