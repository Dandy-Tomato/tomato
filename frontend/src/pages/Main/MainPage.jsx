import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../../components/common/Navbar';
import './MainPage.css';
import tomatoCharacter from '../../assets/tomato_character.png';
import { MdCardTravel, MdAdd, MdRadioButtonChecked, MdPeopleOutline, MdCalendarToday } from 'react-icons/md';
import AlertModal from '../../components/common/AlertModal';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';

/**
 * 서비스의 메인 대시보드 컴포넌트입니다.
 * 내 프로젝트 목록 조회, 새 프로젝트 생성 진입, 기존 프로젝트 참여 기능을 제공합니다.
 */
const MainPage = () => {
    const navigate = useNavigate();
    
    // 사용자가 소속된(참여 중인) 프로젝트 목록 상태
    const [projects, setProjects] = useState([]);
    const [loading, setLoading] = useState(true);
    
    // 참여하기(초대 코드 입력) 모달 상태 관리
    const [isJoinModalOpen, setIsJoinModalOpen] = useState(false);
    const [inviteCodeInput, setInviteCodeInput] = useState('');
    
    // 공통 알림(AlertModal) 상태 관리
    const [modal, setModal] = useState({
        isOpen: false,
        type: 'success',
        title: '',
        message: '',
        onConfirm: null
    });

    /** 알림 모달 출력용 헬퍼 함수 */
    const showAlert = (type, title, message, onConfirm = null) => {
        setModal({ isOpen: true, type, title, message, onConfirm });
    };

    /** 프로젝트 참여하기(초대 코드) 요청 핸들러 */
    const handleJoinProject = async () => {
        if (!inviteCodeInput.trim()) {
            showAlert('error', '입력 오류', '초대 코드를 입력해 주세요.');
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
                // 성공 시 모달을 닫고 프로젝트 목록을 새로고침합니다.
                setIsJoinModalOpen(false);
                setInviteCodeInput('');
                showAlert('success', '참여 완료', "프로젝트 참여에 성공했습니다!", () => fetchMyProjects());
            } else {
                showAlert('error', '참여 실패', result.message || "프로젝트 참여에 실패했습니다.");
            }
        } catch (error) {
            console.error("Error joining project:", error);
            showAlert('error', '서버 오류', "서버 오류가 발생했습니다.");
        }
    };

    // 마운트 시 최초 1회 프로젝트 목록을 서버로부터 가져옵니다.
    useEffect(() => {
        fetchMyProjects();
    }, []);

    /** 내 프로젝트 목록 조회 API 요청 핸들러 */
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

            if (response.ok && result?.data?.content) {
                setProjects(Array.isArray(result.data.content) ? result.data.content : []);
            } else {
                setProjects([]);
            }
        } catch (error) {
            console.error("Error fetching my projects:", error);
            setProjects([]);
        } finally {
            setLoading(false);
        }
    };

    /** 
     * 시작일과 종료일을 입력받아 진행(예상) 주차를 계산해 주는 유틸성 함수 
     * @param {string} start 시작 Date 문자열
     * @param {string} end 종료 Date 문자열
     * @returns {number} 주차 단위 (최소 1주)
     */
    const calculateWeeks = (start, end) => {
        if (!start || !end) return 0;
        try {
            const startDate = new Date(start);
            const endDate = new Date(end);
            if (isNaN(startDate) || isNaN(endDate)) return 0;
            const diffTime = Math.abs(endDate - startDate);
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
            return Math.floor(diffDays / 7) || 1;
        } catch (e) {
            return 0;
        }
    };

    /** 프로젝트 생성 페이지 진입 핸들러 */
    const handleCreateProject = () => {
        navigate('/projects/create');
    };

    /** 개별 프로젝트 상세 페이지 진입 핸들러 */
    const handleProjectDetail = (projectId) => {
        navigate(`/projects/${projectId}`);
    };

    return (
        <div className="main-page">
            <Navbar />

            <main className="main-content">
                {/* 상단 배너 영역 */}
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

                {/* 액션 버튼 그룹: 프로젝트 참여 및 생성 */}
                <section className="action-section">
                    <button className="action-button secondary" onClick={() => setIsJoinModalOpen(true)}>
                        <MdCardTravel className="button-icon" /> 프로젝트 참여하기
                    </button>
                    <button className="action-button primary" onClick={handleCreateProject}>
                        <MdAdd className="button-icon" /> 새 프로젝트 생성하기
                    </button>
                </section>

                {/* 초대 코드 입력 모달 UI */}
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

                {/* 공통 알림 모달 위젯 적용 */}
                <AlertModal 
                    isOpen={modal.isOpen}
                    type={modal.type}
                    title={modal.title}
                    message={modal.message}
                    onClose={() => setModal(prev => ({ ...prev, isOpen: false }))}
                    onConfirm={modal.onConfirm}
                />

                {/* 내 프로젝트 목록 표시 영역 */}
                <section className="project-section">
                    <div className="section-header">
                        <MdRadioButtonChecked className="section-header-icon" />
                        <h2 className="section-title">
                            현재 참여하고 있는 프로젝트 <span className="count">({loading ? '...' : projects.length}개)</span>
                        </h2>
                    </div>

                    {loading ? (
                        <div className="loading-state">로딩 중...</div>
                    ) : projects.length > 0 ? (
                        <div className="project-grid">
                            {projects.map(project => (
                                <div
                                    key={project?.projectId || Math.random()}
                                    className="project-card"
                                    onClick={() => handleProjectDetail(project.projectId)}
                                >
                                    <h3 className="card-title">{project?.name || '제목 없음'}</h3>
                                    <p className="card-date">
                                        {(project?.startedAt || '').toString().replace(/-/g, '.')} ~ {(project?.dueAt || '').toString().replace(/-/g, '.')}
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
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="empty-project">
                            <p className="empty-text">현재 참여하고 있는 프로젝트가 없어요!</p>
                            <p className="empty-subtext">새로운 주제를 추천받거나 직접 프로젝트를 생성해볼까요?</p>
                            <button className="action-button primary" onClick={handleCreateProject} style={{ marginTop: '30px', padding: '0 48px', minHeight: '64px', fontSize: '18px', borderRadius: '16px' }}>
                                <MdAdd className="button-icon" style={{ fontSize: '24px' }} /> 프로젝트 시작하기
                            </button>
                        </div>
                    )}
                </section>
            </main>
        </div>
    );
};

export default MainPage;
