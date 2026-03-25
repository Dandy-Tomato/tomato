import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './Navbar.css';
import tomatoLogo from '../tomato_character.png';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';

const Navbar = () => {
    const navigate = useNavigate();

    // 닉네임 유효성 검사 및 정제 함수
    const getValidNickname = (name) => {
        if (!name || name === 'null' || name === 'undefined') return '멋쟁이 토마토';
        return name;
    };

    const [nickname, setNickname] = useState(getValidNickname(localStorage.getItem('nickname')));

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
                        localStorage.setItem('nickname', newName);
                    }
                })
                .catch(err => console.error("Failed to fetch nickname in Navbar:", err));
        } else {
            setNickname(getValidNickname(storedNickname));
        }
    }, []);

    const handleLogout = async () => {
        const refreshToken = localStorage.getItem('refreshToken');
        const accessToken = localStorage.getItem('accessToken');

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
            localStorage.clear();
            navigate('/');
        }
    };

    return (
        <nav className="navbar">
            <div className="navbar-container">
                <div className="navbar-logo" onClick={() => navigate('/main')}>
                    <img src={tomatoLogo} alt="Tomato Logo" className="logo-icon" />
                    <span className="logo-text">TOMATO</span>
                </div>
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
