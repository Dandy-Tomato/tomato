import React from 'react';
import Navbar from './components/Navbar';
import './MainPage.css';
import tomatoCharacter from './tomato_character.png';
import { MdCardTravel, MdAdd } from 'react-icons/md';

const MainPage = () => {
    // 임시 목 데이터 (나중에 API 연동 가능)
    const projects = []; // 비어있는 상태 테스트용
    // const projects = [
    //     { id: 1, title: "싸피 특화 프로젝트", date: "2026.02.09 - 2026.03.30", leader: "멋쟁이~", members: 6, duration: "6주" },
    //     { id: 2, title: "싸피 특화 프로젝트", date: "2026.02.09 - 2026.03.30", leader: "멋쟁이~", members: 6, duration: "6주" },
    //     { id: 3, title: "싸피 특화 프로젝트", date: "2026.02.09 - 2026.03.30", leader: "멋쟁이~", members: 6, duration: "6주" },
    // ];

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
                    <button className="action-button primary">
                        <MdAdd className="button-icon" /> 새 프로젝트 생성하기
                    </button>
                </section>

                <section className="project-section">
                    <div className="section-header">
                        <span className="section-dot"></span>
                        <h2 className="section-title">현재 참여하고 있는 프로젝트 <span className="count">({projects.length}개)</span></h2>
                    </div>

                    {projects.length > 0 ? (
                        <div className="project-grid">
                            {projects.map(project => (
                                <div key={project.id} className="project-card">
                                    <h3 className="card-title">{project.title}</h3>
                                    <p className="card-date">{project.date}</p>
                                    <p className="card-leader">{project.leader}</p>
                                    <div className="card-info">
                                        <span>6명 / 6주</span>
                                    </div>
                                    <button className="detail-button">자세히 보기</button>
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
                            <button className="start-button">프로젝트 시작하기</button>
                        </div>
                    )}
                </section>
            </main>
        </div>
    );
};

export default MainPage;
