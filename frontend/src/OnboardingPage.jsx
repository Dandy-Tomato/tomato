import React from 'react';

const OnboardingPage = () => {
    return (
        <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
            <h1>온보딩 페이지</h1>
            <p>추가 정보를 입력해 주세요.</p>
            {/* 온보딩 폼 구현 예정 */}
            <button onClick={() => window.location.href = "/main"}>메인으로 가기 (임시)</button>
        </div>
    );
};

export default OnboardingPage;
