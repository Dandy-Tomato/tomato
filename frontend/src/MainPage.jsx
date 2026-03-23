import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import './MainPage.css';
import tomatoCharacter from './tomato_character.png';
import { MdCardTravel, MdAdd } from 'react-icons/md';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';

const MainPage = () => {
    const navigate = useNavigate();
    const [projects, setProjects] = useState([]);
    const [loading, setLoading] = useState(true);

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
                    <button className="action-button secondary">
                        <MdCardTravel className="button-icon" /> 프로젝트 참여하기
                    </button>
                    <button className="action-button primary" onClick={handleCreateProject}>
                        <MdAdd className="button-icon" /> 새 프로젝트 생성하기
                    </button>
                </section>

                <section className="project-section">
                    <div className="section-header">
                        <span className="section-dot"></span>
                        <h2 className="section-title">현재 참여하고 있는 프로젝트 <span className="count">({loading ? '...' : projects.length}개)</span></h2>
                    </div>

                    {loading ? (
                        <div className="loading-state">로딩 중...</div>
                    ) : projects.length > 0 ? (
                        <div className="project-grid">
                            {projects.map(project => (
                                <div key={project.projectId} className="project-card">
                                    <div className="role-badge">{project.projectRole === 'OWNER' ? '팀장' : '팀원'}</div>
                                    <h3 className="card-title">{project.name}</h3>
                                    <p className="card-date">{project.startedAt} - {project.dueAt}</p>
                                    <div className="card-info">
                                        <span>인원: {project.memberCount}명</span>
                                        <span className={`status-badge ${project.topicState ? 'active' : ''}`}>
                                            {project.topicState ? '주제 확정' : '주제 모집 중'}
                                        </span>
                                    </div>
                                    <button className="detail-button" onClick={() => handleProjectDetail(project.projectId)}>자세히 보기</button>
                                </div>
                            ))}
                        </div>
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
