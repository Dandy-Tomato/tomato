import React from 'react';

const MainPage = () => {
    return (
        <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
            <h1>메인 페이지</h1>
            <p>환영합니다! 로그인이 성공적으로 완료되었습니다.</p>
            <button onClick={() => {
                localStorage.clear();
                window.location.href = "/";
            }}>로그아웃</button>
        </div>
    );
};

export default MainPage;
