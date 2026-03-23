import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import './MainPage.css';
import tomatoCharacter from './tomato_character.png';
import { MdCardTravel, MdAdd, MdRadioButtonChecked, MdPeopleOutline, MdCalendarToday } from 'react-icons/md';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';

const MainPage = () => {
    const navigate = useNavigate();
    const [projects, setProjects] = useState([]);
    const [loading, setLoading] = useState(true);
    const [isJoinModalOpen, setIsJoinModalOpen] = useState(false);
    const [inviteCodeInput, setInviteCodeInput] = useState('');

    const handleJoinProject = async () => {
        if (!inviteCodeInput.trim()) {
            alert("초대 코드를 입력해 주세요.");
            return;
        }

        const token = localStorage.getItem("accessToken");
        try {
            const response = await fetch(`${API_BASE_URL}/projects/join`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ inviteCode: inviteCodeInput })
            });
            const result = await response.json();
            if (response.ok) {
                alert("프로젝트 참여에 성공했습니다!");
                setIsJoinModalOpen(false);
                setInviteCodeInput('');
                fetchMyProjects(); // 목록 갱신
            } else {
                alert(result.message || "프로젝트 참여에 실패했습니다.");
            }
        } catch (error) {
            console.error("Error joining project:", error);
            alert("서버 오류가 발생했습니다.");
        }
    };

    useEffect(() => {
        fetchMyProjects();
    }, []);

    const fetchMyProjects = async () => {
        const token = localStorage.getItem("accessToken");
        if (!token) {
            setLoading(false);
            return;
        }

        try {
            const response = await fetch(`${API_BASE_URL}/projects/me?page=0&size=10`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            const result = await response.json();
            console.log("My Projects API Result:", result);

            if (response.ok && result.data && result.data.content) {
                setProjects(result.data.content);
            }
        } catch (error) {
            console.error("Error fetching my projects:", error);
        } finally {
            setLoading(false);
        }
    };

    const calculateWeeks = (start, end) => {
        if (!start || !end) return 0;
        const startDate = new Date(start);
        const endDate = new Date(end);
        const diffTime = Math.abs(endDate - startDate);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        return Math.floor(diffDays / 7) || 1;
    };

    const handleCreateProject = () => {
        navigate('/projects/create');
    };

    const handleProjectDetail = (projectId) => {
        navigate(`/projects/${projectId}`);
    };

    return (
        <div className="main-page">
            <Navbar />

            <main className="main-content">
                <section className="banner-section">
                    <div className="banner-card">
                        <img src={tomatoCharacter} alt="Tomato Character" className="banner-image" />
                        <p className="banner-subtitle">토픽 매칭 토탈플랫폼</p>
                        <h1 className="banner-title">
                            나에게 딱 맞는<br />
                            <span className="highlight">프로젝트 주제</span>를<br />
                            찾아드릴게요
                        </h1>
                    </div>
                </section>

                <section className="action-section">
                    <button className="action-button secondary" onClick={() => setIsJoinModalOpen(true)}>
                        <MdCardTravel className="button-icon" /> 프로젝트 참여하기
                    </button>
                    <button className="action-button primary" onClick={handleCreateProject}>
                        <MdAdd className="button-icon" /> 새 프로젝트 생성하기
                    </button>
                </section>

                {/* 초대 코드 입력 모달 */}
                {isJoinModalOpen && (
                    <div className="modal-overlay" onClick={() => setIsJoinModalOpen(false)}>
                        <div className="join-modal" onClick={(e) => e.stopPropagation()}>
                            <h2 className="modal-title">초대 코드 입력</h2>
                            <p className="modal-desc">참여하려는 프로젝트의 초대 코드를 입력해 주세요.</p>
                            <input 
                                type="text" 
                                className="modal-input" 
                                placeholder="초대 코드 (예: RN5B4FRL)"
                                value={inviteCodeInput}
                                onChange={(e) => setInviteCodeInput(e.target.value)}
                                autoFocus
                            />
                            <div className="modal-buttons">
                                <button className="modal-btn cancel" onClick={() => setIsJoinModalOpen(false)}>취소</button>
                                <button className="modal-btn submit" onClick={handleJoinProject}>참여하기</button>
                            </div>
                        </div>
                    </div>
                )}

                <section className="project-section">
                    <div className="section-header">
                        <MdRadioButtonChecked className="section-header-icon" />
                        <h2 className="section-title">현재 참여하고 있는 프로젝트 <span className="count">({loading ? '...' : projects.length}개)</span></h2>
                    </div>

                    {loading ? (
                        <div className="loading-state">로딩 중...</div>
                    ) : projects.length > 0 ? (
                        <>
                            <div className="project-grid">
                                {projects.map(project => (
                                    <div key={project.projectId} className="project-card">
                                        <h3 className="card-title">{project.name}</h3>
                                        <p className="card-date">
                                            {project.startedAt?.replace(/-/g, '.')} ~ {project.dueAt?.replace(/-/g, '.')}
                                        </p>
                                        <div className="card-stats">
                                            <span className="stat-item">
                                                <MdPeopleOutline className="stat-icon" /> {project.memberCount}명
                                            </span>
                                            <span className="stat-sep">/</span>
                                            <span className="stat-item">
                                                <MdCalendarToday className="stat-icon" /> {calculateWeeks(project.startedAt, project.dueAt)}주
                                            </span>
                                        </div>
                                        <button className="card-detail-btn" onClick={() => handleProjectDetail(project.projectId)}>
                                            자세히 보기
                                        </button>
                                    </div>
                                ))}
                            </div>
                            <div className="discovery-footer">
                                <div className="footer-line"></div>
                                <button className="discovery-more-btn">
                                    <MdAdd className="btn-icon" /> 더보기
                                </button>
                            </div>
                        </>
                    ) : (
                        <div className="empty-project">
                            <div className="empty-icon-container">
                                <span className="rocket-icon">🚀</span>
                            </div>
                            <p className="empty-text">현재 참여하고 있는 프로젝트가 없어요!</p>
                            <p className="empty-subtext">새로운 주제를 추천받거나 직접 프로젝트를 생성해볼까요?</p>
                            <button className="start-button" onClick={handleCreateProject}>프로젝트 시작하기</button>
                        </div>
                    )}
                </section>
            </main>
        </div>
    );
};

export default MainPage;
