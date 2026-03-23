import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import './ProjectDetailPage.css';
import { SKILLS, DOMAINS, POSITIONS } from './constants';
import { 
    MdEdit, MdContentCopy, MdKeyboardArrowDown, MdKeyboardArrowUp,
    MdAutoAwesome, MdSearch, MdBookmarkBorder, MdHistory, MdBookmark,
    MdAdd, MdPeopleOutline, MdPersonAdd
} from 'react-icons/md';
import AlertModal from './components/AlertModal';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';

const ProjectDetailPage = () => {
    const { projectId } = useParams();
    const navigate = useNavigate();
    const [project, setProject] = useState(null);
    const [loading, setLoading] = useState(true);
    const [isDetailsOpen, setIsDetailsOpen] = useState(true);
    const [activeTab, setActiveTab] = useState('추천 주제');
    const [recommendations, setRecommendations] = useState([]);
    const [modal, setModal] = useState({
        isOpen: false,
        type: 'success',
        title: '',
        message: '',
        onConfirm: null,
        showCancel: false
    });

    const showAlert = (type, title, message, onConfirm = null, showCancel = false) => {
        setModal({ isOpen: true, type, title, message, onConfirm, showCancel });
    };

    const currentUserId = Number(localStorage.getItem('userId'));

    useEffect(() => {
        fetchProjectDetail();
        fetchRecommendations();
    }, [projectId]);

    const fetchProjectDetail = async () => {
        const token = localStorage.getItem("accessToken");
        try {
            const response = await fetch(`${API_BASE_URL}/projects/${projectId}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const result = await response.json();
            if (response.ok && result.data) {
                setProject(result.data);
            } else {
                showAlert('error', '오류', "프로젝트 정보를 불러오지 못했습니다.", () => navigate('/main'));
            }
        } catch (error) {
            console.error("Error fetching project detail:", error);
        } finally {
            setLoading(false);
        }
    };

    const fetchRecommendations = async () => {
        const token = localStorage.getItem("accessToken");
        try {
            const response = await fetch(`${API_BASE_URL}/projects/${projectId}/recommendations`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const result = await response.json();
            if (response.ok && result.data) {
                setRecommendations(result.data);
            }
        } catch (error) {
            console.error("Error fetching recommendations:", error);
        }
    };

    const copyInviteCode = async () => {
        const token = localStorage.getItem("accessToken");
        try {
            const response = await fetch(`${API_BASE_URL}/projects/${projectId}/invite-code`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const result = await response.json();
            if (response.ok && result.data?.inviteCode) {
                await navigator.clipboard.writeText(result.data.inviteCode);
                showAlert('success', '복사 완료!', '초대 코드가 클립보드에 복사되었습니다.\n팀원들에게 공유해 보세요.');
            } else {
                showAlert('error', '복사 실패', "초대 코드를 가져오지 못했습니다.");
            }
        } catch (error) {
            console.error("Error fetching invite code:", error);
            showAlert('error', '오류', "초대 코드 복사 중 오류가 발생했습니다.");
        }
    };

    const handleLeaveProject = () => {
        showAlert('info', '프로젝트 나가기', "정말로 이 프로젝트에서 나가시겠습니까?", () => executeLeaveProject(), true);
    };

    const executeLeaveProject = async () => {
        const token = localStorage.getItem("accessToken");
        try {
            const response = await fetch(`${API_BASE_URL}/projects/${projectId}/members`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const result = await response.json();
            
            if (response.ok) {
                showAlert('success', '탈퇴 완료', "프로젝트에서 성공적으로 나갔습니다.", () => navigate('/main'));
            } else {
                showAlert('error', '나가기 실패', result.message || "프로젝트 나가기에 실패했습니다.");
            }
        } catch (error) {
            console.error("Error leaving project:", error);
            showAlert('error', '서버 오류', "서버 오류가 발생했습니다.");
        }
    };

    if (loading) return <div className="loading">로딩 중...</div>;
    if (!project) return null;

    const isOwner = project.owner.userId === currentUserId;
    const getDomainName = (id) => DOMAINS.find(d => d.id === id)?.name || id;
    const getPositionName = (id) => POSITIONS.find(p => p.id === id)?.name || '기타';

    return (
        <div className="project-detail-page">
            <Navbar />
            <main className="project-detail-content">
                
                {/* 프로젝트 헤더 카드 */}
                <div className="project-header-card">
                    <div className="header-main">
                        <div className="header-left">
                            <div className="title-row" onClick={() => setIsDetailsOpen(!isDetailsOpen)}>
                                <h1 className="project-name">{project.name}</h1>
                                {isDetailsOpen ? <MdKeyboardArrowUp className="toggle-icon" /> : <MdKeyboardArrowDown className="toggle-icon" />}
                            </div>
                            <p className="project-meta">{project.startedAt} - {project.dueAt}</p>
                            <p className="project-owner">{project.owner.nickname}~</p>
                        </div>
                        <div className="header-right">
                            <div className="member-count-badge">
                                <MdPeopleOutline className="m-icon" /> <span>{project.memberCount}명</span>
                            </div>
                            <button className="copy-code-button" onClick={copyInviteCode}>
                                <MdPersonAdd className="btn-icon" /> 초대코드 복사하기
                            </button>
                            {isOwner && (
                                <button className="edit-icon-button" onClick={() => navigate(`/projects/create?edit=${projectId}`)}>
                                    <MdEdit />
                                </button>
                            )}
                        </div>
                    </div>

                    {isDetailsOpen && (
                        <div className="header-details">
                            <div className="domain-section">
                                <p className="detail-label">도메인</p>
                                <div className="detail-tags">
                                    {project.domains.map(id => (
                                        <span key={id} className="detail-tag">{getDomainName(id)}</span>
                                    ))}
                                </div>
                            </div>
                            <div className="members-section">
                                <p className="detail-label">참여자</p>
                                <div className="member-cards-grid">
                                    {project.members.map(member => (
                                        <div key={member.userId} className="member-small-card">
                                            <span className="m-name">{member.nickname || '익명'}</span>
                                            <span className="m-pos">{getPositionName(member.positionId)}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                            {!isOwner && (
                                <div className="detail-footer">
                                    <button className="leave-project-link" onClick={handleLeaveProject}>프로젝트 나가기</button>
                                </div>
                            )}
                        </div>
                    )}
                </div>

                {/* 추천 주제 섹션 */}
                <div className="recommend-container">
                    <aside className="recommend-sidebar">
                        <div 
                            className={`sidebar-item ${activeTab === '추천 주제' ? 'active' : ''}`}
                            onClick={() => setActiveTab('추천 주제')}
                        >
                            <MdAutoAwesome className="s-icon" /> 추천 주제
                        </div>
                        <div className="sidebar-item"><MdSearch className="s-icon" /> 주제 검색</div>
                        <div className="sidebar-item"><MdBookmarkBorder className="s-icon" /> 북마크</div>
                        <div className="sidebar-item"><MdHistory className="s-icon" /> 히스토리</div>
                    </aside>

                    <section className="recommend-main">
                        <div className="recommend-header">
                            <h2 className="recommend-title">{activeTab}</h2>
                            <span className="recommend-count">6 / 30</span>
                        </div>

                        <div className="topic-grid">
                            {recommendations.map(topic => (
                                <div key={topic.topicId} className="topic-card">
                                    <div className="topic-card-header">
                                        <h3 className="topic-title">{topic.title}</h3>
                                        {topic.bookmarked ? <MdBookmark className="bookmark-icon active" /> : <MdBookmarkBorder className="bookmark-icon" />}
                                    </div>
                                    <div className="topic-domain-tag">{topic.domainName}</div>
                                    <div className="topic-footer">
                                        <div className="topic-skills">
                                            {topic.skills.map(s => <span key={s} className="t-skill-tag">{s}</span>)}
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                        
                        <div className="more-button-container">
                            <button className="more-btn"><MdAdd className="btn-icon" /> 더보기</button>
                        </div>
                    </section>
                </div>

                <AlertModal 
                    isOpen={modal.isOpen}
                    type={modal.type}
                    title={modal.title}
                    message={modal.message}
                    onClose={() => setModal(prev => ({ ...prev, isOpen: false }))}
                    onConfirm={modal.onConfirm}
                    showCancel={modal.showCancel}
                />
            </main>
        </div>
    );
};

export default ProjectDetailPage;
