import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './Navbar.css';

// 상위 assets 경로 내 이미지 참조로 수정
import tomatoLogo from '../../assets/tomato_character.png';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';

/**
 * 상단 네비게이션 바 컴포넌트입니다.
 * 사용자 닉네임 표시 및 로그아웃과 같은 전역적인 기능들을 포함합니다.
 */
const Navbar = () => {
    const navigate = useNavigate();

    /**
     * 유효하지 않은 닉네임 문자열에 대한 방어 로직입니다.
     * 값이 비어있거나 구문상 'null'일 경우 기본값 부여
     * @param {string} name - 정제할 닉네임 문자열
     * @returns 정제된 닉네임 문자열
     */
    const getValidNickname = (name) => {
        if (!name || name === 'null' || name === 'undefined') return '멋쟁이 토마토';
        return name;
    };

    // 현재 접속한 사용자의 닉네임을 로컬 스토리지 정보 기반으로 상태 선언
    const [nickname, setNickname] = useState(getValidNickname(localStorage.getItem('nickname')));

    /**
     * 컴포넌트 마운트 시, 닉네임 정보가 스토리지에 없으면 
     * 백엔드 API에서 조회한 뒤 스토리지 및 상태에 갱신해 줍니다.
     */
    useEffect(() => {
        const storedNickname = localStorage.getItem('nickname');
        const token = localStorage.getItem('accessToken');

        if ((!storedNickname || storedNickname === 'null') && token) {
            fetch(`${API_BASE_URL}/users/profile`, {
                headers: { 'Authorization': `Bearer ${token}` }
            })
                .then(res => res.json())
                .then(result => {
                    console.log("Navbar Profile API Result:", result);
                    if (result.data && result.data.nickname) {
                        const newName = getValidNickname(result.data.nickname);
                        setNickname(newName);
                        // 새로 갱신한 닉네임을 캐싱 목적으로 로컬 스토리지에 저장합니다.
                        localStorage.setItem('nickname', newName);
                    }
                })
                .catch(err => console.error("Failed to fetch nickname in Navbar:", err));
        } else {
            setNickname(getValidNickname(storedNickname));
        }
    }, []);

    /**
     * 로그아웃 처리 핸들러
     * 백엔드에 토큰 무효화를 요청하고 로컬 스토리지를 비운 후 로그인 페이지로 이동합니다.
     */
    const handleLogout = async () => {
        const refreshToken = localStorage.getItem('refreshToken');
        const accessToken = localStorage.getItem('accessToken');

        // 리프레시 토큰이 없으면 이미 로그아웃된(또는 만료된) 것으로 간주하고 클라이언트 처리만 진행
        if (!refreshToken) {
            localStorage.clear();
            navigate('/');
            return;
        }

        try {
            const response = await fetch(`${API_BASE_URL}/auth/logout`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${accessToken}`
                },
                body: JSON.stringify({ refreshToken })
            });

            if (response.ok) {
                console.log("Logout successful");
            } else {
                console.warn("Logout API failed or token invalid");
            }
        } catch (error) {
            console.error("Logout error:", error);
        } finally {
            // 성공하든 실패하든 클라이언트의 세션 정보는 모두 제거
            localStorage.clear();
            navigate('/');
        }
    };

    return (
        <nav className="navbar">
            <div className="navbar-container">
                {/* 로고 영역: 클릭 시 메인 대시보드로 이동 */}
                <div className="navbar-logo" onClick={() => navigate('/main')}>
                    <img src={tomatoLogo} alt="Tomato Logo" className="logo-icon" />
                    <span className="logo-text">TOMATO</span>
                </div>
                
                {/* 네비게이션 우측: 사용자 정보 표시 및 로그아웃 버튼 */}
                <div className="navbar-right">
                    <div className="navbar-user">
                        <span className="welcome-text">
                            안녕하세요, <span
                                className="nickname-link"
                                onClick={() => navigate('/profile')}
                            >
                                {nickname} 님!
                            </span>
                        </span>
                    </div>
                    <button className="logout-button" onClick={handleLogout}>로그아웃</button>
                </div>
            </div>
        </nav>
    );
};

export default Navbar;
