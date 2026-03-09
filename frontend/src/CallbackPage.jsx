import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const CallbackPage = () => {
    const navigate = useNavigate();

    useEffect(() => {
        // window.location.hash에서 파라미터 파싱 (#accessToken=...&refreshToken=...&isOnboarding=...)
        const hash = window.location.hash.substring(1);
        const params = new URLSearchParams(hash);

        const accessToken = params.get("accessToken");
        const refreshToken = params.get("refreshToken");
        const isOnboarding = params.get("isOnboarding");

        if (accessToken && refreshToken) {
            // 토큰 저장 (localStorage 또는 세션 관리 전략에 따라 변경 가능)
            localStorage.setItem("accessToken", accessToken);
            localStorage.setItem("refreshToken", refreshToken);

            // 사용자 상태에 따라 페이지 이동
            if (isOnboarding === "false") {
                // 온보딩 필요 -> 통합된 SignupPage의 2단계로 이동
                navigate("/signup?isSocial=true");
            } else {
                // 온보딩 완료 -> 메인 페이지 이동
                navigate("/main");
            }
        } else {
            // 토큰이 없는 경우 로그인 페이지로 리다이렉트 (에러 처리)
            console.error("Authentication failed: No tokens found in hash.");
            navigate("/");
        }
    }, [navigate]);

    return (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
            <p>로그인 중입니다. 잠시만 기다려주세요...</p>
        </div>
    );
};

export default CallbackPage;
