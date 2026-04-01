import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

/**
 * 소셜 로그인(OAuth 콜백) 처리용 컴포넌트입니다.
 * 백엔드 인증 후 리다이렉트되어 파라미터로 넘어온 토큰 정보를 로컬 스토리지에 저장하고,
 * 온보딩(추가 정보 입력) 여부에 따라 페이지를 이동시킵니다.
 */
const CallbackPage = () => {
    const navigate = useNavigate();

    useEffect(() => {
        // window.location.hash에서 파라미터 파싱 (#accessToken=...&refreshToken=...&isOnboarding=...)
        const hash = window.location.hash.substring(1);
        console.log("Callback hash:", hash); // 디버깅용

        const params = new URLSearchParams(hash);
        const accessToken = params.get("accessToken");
        const refreshToken = params.get("refreshToken");
        const isOnboarding = params.get("isOnboarding");

        console.log("Parsed params:", { accessToken, refreshToken, isOnboarding }); // 디버깅용

        // URL 파라미터로 넘겨받은 토큰 정보가 모두 존재한다면 스토리지에 저장
        if (accessToken && refreshToken) {
            localStorage.setItem("accessToken", accessToken);
            localStorage.setItem("refreshToken", refreshToken);

            console.log("Tokens saved. Navigating based on isOnboarding:", isOnboarding);

            // 사용자 온보딩(최초 가입 시 추가 정보 입력) 상태에 따라 페이지 분기 처리
            if (isOnboarding === "false") {
                // 온보딩이 안 된 신규 유저 -> 소셜 회원가입 모드임을 명시하여 회원가입 2단계로 이동
                navigate("/signup?isSocial=true");
            } else {
                // 온보딩 완료된 기존 유저 -> 닉네임 및 사용자 ID 등 추가 정보를 가져와 저장한 뒤 메인 페이지로 이동
                const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';
                fetch(`${API_BASE_URL}/users/profile`, {
                    headers: { 'Authorization': `Bearer ${accessToken}` }
                })
                    .then(res => res.json())
                    .then(result => {
                        if (result.data) {
                            // 닉네임 캐싱 (오류 방어 로직 포함)
                            if (result.data.nickname && result.data.nickname !== "null") {
                                localStorage.setItem("nickname", result.data.nickname);
                            }
                            // 유저 ID 정보 캐싱
                            if (result.data.user_id || result.data.userId) {
                                localStorage.setItem("userId", result.data.user_id || result.data.userId);
                            }
                        }
                        // 프로필 정보를 다 받아온 뒤 메인 페이지로 정상 진입
                        navigate("/main");
                    })
                    .catch(err => {
                        console.error("Failed to fetch profile in callback:", err);
                        navigate("/main");
                    });
            }
        } else {
            // 전달받은 토큰 정보가 없는 비정상적인 접근인 경우 에러 처리
            console.error("Authentication failed: No tokens found in hash.");
            // navigate("/"); // 문제가 발생했을 때 메인으로 리다이렉트 (필요 시 주석 해제)
        }
    }, [navigate]);

    return (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
            <p>로그인 중입니다. 잠시만 기다려주세요...</p>
        </div>
    );
};

export default CallbackPage;
