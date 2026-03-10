import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import './ProfilePage.css';
import { MdPerson, MdCode, MdBusiness, MdSearch } from 'react-icons/md';
import { POSITIONS, SKILLS, DUMMY_COMPANIES } from './constants';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';

const ProfilePage = () => {
    const [isEditing, setIsEditing] = useState(false);
    const [loading, setLoading] = useState(true);
    const [profile, setProfile] = useState({
        email: '',
        nickname: '',
        githubUsername: '',
        positionId: null,
        skillIds: [],
        companyIds: []
    });

    useEffect(() => {
        fetchProfile();
    }, []);

    const fetchProfile = async () => {
        const token = localStorage.getItem("accessToken");
        if (!token) {
            alert("로그인이 필요합니다.");
            window.location.href = "/";
            return;
        }

        try {
            const response = await fetch(`${API_BASE_URL}/users/profile`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            const result = await response.json();
            console.log("Profile Page API Result:", result);

            if (response.ok && result.data) {
                const data = result.data;
                setProfile({
                    email: data.email || '',
                    nickname: data.nickname || '',
                    githubUsername: data.githubUsername || '',
                    positionId: data.position || null, // API에서는 position으로 옴
                    skillIds: data.skillIds || [],
                    companyIds: data.companyIds || []
                });
                if (data.nickname && data.nickname !== "null") {
                    localStorage.setItem('nickname', data.nickname);
                }
            } else {
                console.error("Failed to fetch profile:", result.message);
            }
        } catch (error) {
            console.error("Error fetching profile:", error);
        } finally {
            setLoading(false);
        }
    };

    const handleEditToggle = () => setIsEditing(!isEditing);

    const handleSave = async () => {
        const token = localStorage.getItem("accessToken");
        const body = {
            nickname: profile.nickname,
            githubUsername: profile.githubUsername || null,
            positionId: profile.positionId || null,
            companyIds: profile.companyIds,
            skillIds: profile.skillIds
        };

        try {
            const response = await fetch(`${API_BASE_URL}/auth/onboarding`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(body)
            });

            if (response.ok) {
                alert("프로필이 수정되었습니다.");
                setIsEditing(false);
                fetchProfile(); // 최신 데이터 다시 불러오기
            } else {
                const result = await response.json();
                alert(result.message || "수정에 실패했습니다.");
            }
        } catch (error) {
            console.error("Error updating profile:", error);
            alert("서버 오류가 발생했습니다.");
        }
    };

    if (loading) return <div className="loading">로딩 중...</div>;

    // ID를 이름으로 변환하는 도움 함수들
    const getPositionName = (id) => POSITIONS.find(p => p.id === id)?.name || '없음';
    const getSkillName = (id) => SKILLS.find(s => s.id === id)?.name || id;
    const getCompanyName = (id) => DUMMY_COMPANIES.find(c => c.id === id)?.name || id;

    return (
        <div className="profile-page">
            <Navbar />
            <main className="profile-content">

                {/* 기본 정보 섹션 */}
                <section className="profile-card">
                    <div className="card-header">
                        <h2 className="card-title">기본 정보</h2>
                        <MdPerson className="header-icon" />
                    </div>
                    <div className="info-list">
                        <div className="info-item">
                            <span className="info-label">이메일</span>
                            <span className="info-value">{profile.email}</span>
                        </div>
                        <div className="info-item">
                            <span className="info-label">닉네임</span>
                            {isEditing ? (
                                <input
                                    className="edit-input"
                                    value={profile.nickname}
                                    onChange={(e) => setProfile({ ...profile, nickname: e.target.value })}
                                />
                            ) : (
                                <span className="info-value">{profile.nickname}</span>
                            )}
                        </div>
                        <div className="info-item">
                            <span className="info-label">GitHub</span>
                            {isEditing ? (
                                <input
                                    className="edit-input"
                                    value={profile.githubUsername}
                                    onChange={(e) => setProfile({ ...profile, githubUsername: e.target.value })}
                                    placeholder="github.com/username"
                                />
                            ) : (
                                <span className="info-value link">{profile.githubUsername || '등록된 계정 없음'}</span>
                            )}
                        </div>
                    </div>
                </section>

                {/* 기술 스택 섹션 */}
                <section className="profile-card">
                    <div className="card-header">
                        <h2 className="card-title">기술 스택</h2>
                        <MdCode className="header-icon" />
                    </div>
                    <div className="stack-content">
                        <p className="stack-label">직무</p>
                        <div className="position-tags">
                            {POSITIONS.map(pos => (
                                <button
                                    key={pos.id}
                                    className={`tag-button ${profile.positionId === pos.id ? 'active' : ''}`}
                                    disabled={!isEditing}
                                    onClick={() => setProfile({ ...profile, positionId: pos.id })}
                                >
                                    {pos.name}
                                </button>
                            ))}
                        </div>

                        <p className="stack-label">보유 기술 스택</p>
                        <div className="skill-tags">
                            {profile.skillIds.map(id => (
                                <span key={id} className="skill-tag">
                                    {getSkillName(id)}
                                    {isEditing && (
                                        <span
                                            className="tag-remove"
                                            onClick={() => setProfile({ ...profile, skillIds: profile.skillIds.filter(s => s !== id) })}
                                        >✕</span>
                                    )}
                                </span>
                            ))}
                        </div>

                        {isEditing && (
                            <div className="skill-search">
                                <p className="stack-label">보유한 기술 스택을 선택해주세요.</p>
                                <div className="search-bar">
                                    <input type="text" placeholder="검색어를 입력하세요." />
                                    <button className="search-button">검색</button>
                                </div>
                            </div>
                        )}
                    </div>
                </section>

                {/* 희망 기업 섹션 */}
                <section className="profile-card">
                    <div className="card-header">
                        <h2 className="card-title">희망 기업</h2>
                        <MdBusiness className="header-icon" />
                    </div>
                    <div className="company-tags">
                        {profile.companyIds.map(id => (
                            <span key={id} className="company-tag">
                                {getCompanyName(id)}
                                {isEditing && (
                                    <span
                                        className="tag-remove"
                                        onClick={() => setProfile({ ...profile, companyIds: profile.companyIds.filter(c => c !== id) })}
                                    >✕</span>
                                )}
                            </span>
                        ))}
                    </div>
                </section>

                <div className="footer-actions">
                    {isEditing ? (
                        <button className="submit-button" onClick={handleSave}>완료</button>
                    ) : (
                        <button className="edit-link" onClick={handleEditToggle}>수정하기</button>
                    )}
                </div>
            </main>
        </div>
    );
};

export default ProfilePage;
