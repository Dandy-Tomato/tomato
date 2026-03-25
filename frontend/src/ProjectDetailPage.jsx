import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import './ProjectDetailPage.css';
import { SKILLS, DOMAINS, POSITIONS } from './constants';
import { 
    MdEdit, MdContentCopy, MdKeyboardArrowDown, MdKeyboardArrowUp,
    MdAutoAwesome, MdSearch, MdBookmarkBorder, MdBookmark,
    MdAdd, MdPeopleOutline, MdPersonAdd, MdThumbUp, MdThumbDown,
    MdArrowBack, MdRefresh, MdLightbulbOutline
} from 'react-icons/md';
import AlertModal from './components/AlertModal';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';

// 주제 상세 보기 컴포넌트
const TopicDetailView = ({ topic, isLoading, onBack, onReaction, onBookmark, getDomainName, getSkillName }) => {
    if (isLoading || !topic) return <div className="topic-detail-loading">데이터를 불러오는 중...</div>;
    const isMarked = topic.isBookmarked === true || topic.isBookmarked === 'true' || 
                     topic.isBookmark === true || topic.isBookmark === 'true' || 
                     topic.bookmarked === true || topic.bookmarked === 'true';

    return (
        <div className="topic-detail-view">
            {/* 상단 헤더 섹션 */}
            <div className="topic-detail-header-card">
                <div className="topic-header-top">
                    <span className="topic-domain-badge">{getDomainName(topic.domainId)}</span>
                    <div className="topic-actions">
                        <button 
                            className={`topic-action-btn ${topic.isReaction === 'LIKE' ? 'active' : ''}`}
                            onClick={() => onReaction(topic.topicId, 'LIKE')}
                        >
                            <MdThumbUp />
                        </button>
                        <button 
                            className={`topic-action-btn ${topic.isReaction === 'DISLIKE' ? 'active' : ''}`}
                            onClick={() => onReaction(topic.topicId, 'DISLIKE')}
                        >
                            <MdThumbDown />
                        </button>
                        <button 
                            className={`topic-action-btn bookmark ${isMarked ? 'active' : ''}`}
                            onClick={() => onBookmark(topic.topicId)}
                        >
                            {isMarked ? <MdBookmark style={{ color: '#ee7c62' }} /> : <MdBookmarkBorder />}
                        </button>
                    </div>
                </div>

                <h1 className="topic-detail-title">{topic.title}</h1>
                
                <div className="topic-detail-skills">
                    {topic.skills.map(id => (
                        <span key={id} className="td-skill-tag">{getSkillName(id)}</span>
                    ))}
                </div>

                <p className="topic-detail-description">{topic.description}</p>

                <div className="topic-metadata-grid">
                    <div className="metadata-item">
                        <span className="meta-label">예상 개발 기간</span>
                        <div className="meta-value-wrap">
                            <span className="meta-icon">📅</span>
                            <span className="meta-value">{topic.expectedDurationWeek || 0}주</span>
                        </div>
                    </div>
                    <div className="metadata-item">
                        <span className="meta-label">추천 팀원 수</span>
                        <div className="meta-value-wrap">
                            <span className="meta-icon">👥</span>
                            <span className="meta-value">{topic.recommendedTeamSize || 0}명</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* 이동 및 구체화 버튼 섹션 */}
            <div className="topic-nav-actions">
                <p className="nav-info-text">마음에 드신다면 AI로 주제를 더 구체화해보세요!</p>
                <div className="nav-buttons">
                    <button className="back-to-list-btn" onClick={onBack}>
                        <MdArrowBack className="btn-icon" /> 목록으로
                    </button>
                    <button className="elaborate-btn" onClick={() => {/* 구체화 API 연동 예정 */}}>
                        <MdAutoAwesome className="btn-icon" /> 구체화하기
                    </button>
                </div>
            </div>

            {/* 구체화 결과 섹션 (데이터가 있을 경우에만 표시) */}
            {topic.elaboration && (
                <div className="elaboration-section">
                    <div className="elab-badge-row">
                        <span className="elab-status-badge"><MdAutoAwesome /> 구체화 완료</span>
                    </div>
                    <h2 className="elab-title">{topic.elaboration.title}</h2>
                    <p className="elab-subtitle">{topic.elaboration.subtitle}</p>

                    <div className="elab-group">
                        <h3 className="elab-group-label">핵심 기능</h3>
                        <div className="feature-list">
                            {topic.elaboration.features.map((feature, index) => (
                                <div key={index} className="feature-item">
                                    <div className="feature-num">{index + 1}</div>
                                    <div className="feature-content">
                                        <h4 className="f-title">{feature.title}</h4>
                                        <p className="f-desc">{feature.description}</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="elab-group">
                        <h3 className="elab-group-label">추천 기술스택</h3>
                        <div className="elab-skill-tags">
                            {topic.elaboration.techStack.map(skill => (
                                <span key={skill} className="e-skill-tag">{skill}</span>
                            ))}
                        </div>
                    </div>

                    <div className="elab-group">
                        <h3 className="elab-group-label">차별화 포인트</h3>
                        <div className="differentiation-card">
                            <MdLightbulbOutline className="diff-icon" />
                            <p className="diff-text">{topic.elaboration.differentiation}</p>
                        </div>
                    </div>

                    <div className="elab-footer">
                        <div className="difficulty-display">
                            <span className="diff-label-text">
                                추천 기간 {topic.elaboration.durationRange}
                            </span>
                        </div>
                        <button className="re-elaborate-btn">
                            <MdRefresh className="btn-icon" /> 다시 구체화
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

const ProjectDetailPage = () => {
    const { projectId } = useParams();
    const navigate = useNavigate();
    const [project, setProject] = useState(null);
    const [loading, setLoading] = useState(true);
    const [isDetailsOpen, setIsDetailsOpen] = useState(true);
    const [activeTab, setActiveTab] = useState('추천 주제');
    const [recommendations, setRecommendations] = useState([]);
    const [visibleCount, setVisibleCount] = useState(6);
    const [selectedTopicId, setSelectedTopicId] = useState(null);
    const [topicDetail, setTopicDetail] = useState(null);
    const [isTopicLoading, setIsTopicLoading] = useState(false);
    const [modal, setModal] = useState({
        isOpen: false,
        type: 'success',
        title: '',
        message: '',
        onConfirm: null,
        showCancel: false
    });
    
    // 타 사용자 프로필 모달 상태
    const [selectedUser, setSelectedUser] = useState(null);
    const [isUserModalOpen, setIsUserModalOpen] = useState(false);
    const [isUserLoading, setIsUserLoading] = useState(false);

    const showAlert = (type, title, message, onConfirm = null, showCancel = false) => {
        setModal({ isOpen: true, type, title, message, onConfirm, showCancel });
    };

    const currentUserId = Number(localStorage.getItem('userId'));

    useEffect(() => {
        fetchProjectDetail();
        fetchRecommendations();
    }, [projectId]);

    useEffect(() => {
        if (selectedTopicId) {
            fetchTopicDetail(selectedTopicId);
        } else {
            setTopicDetail(null);
        }
    }, [selectedTopicId]);

    const fetchProjectDetail = async () => {
        const token = localStorage.getItem("accessToken");
        try {
            const response = await fetch(`${API_BASE_URL}/projects/${projectId}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const result = await response.json();
            if (response.ok && result.data) {
                console.log("Fetched Project Detail:", result.data);
                console.log("Project Members:", result.data.members);
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
            console.log("Recommendations List API Result:", result);
            
            if (response.ok && result.data) {
                const dataArray = Array.isArray(result.data) 
                    ? result.data 
                    : (result.data.content || []);
                setRecommendations(dataArray);
            }
        } catch (error) {
            console.error("Error fetching recommendations:", error);
        }
    };

    const fetchTopicDetail = async (topicId) => {
        setIsTopicLoading(true);
        const token = localStorage.getItem("accessToken");
        try {
            const response = await fetch(`${API_BASE_URL}/projects/${projectId}/recommendations/${topicId}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            
            if (response.status === 403) {
                showAlert('error', '권한 없음', '해당 프로젝트에 접근 권한이 없습니다.');
                setSelectedTopicId(null);
                return;
            } else if (response.status === 404) {
                showAlert('error', '오류', '프로젝트를 찾을 수 없습니다.');
                setSelectedTopicId(null);
                return;
            } else if (response.status === 500) {
                showAlert('error', '서버 오류', '추천 서버 호출에 실패했습니다.');
                setSelectedTopicId(null);
                return;
            }

            const result = await response.json();
            console.log("Topic Detail API Result:", result);

            if (response.ok && result.data) {
                setTopicDetail(Array.isArray(result.data) ? result.data[0] : result.data);
            } else {
                showAlert('error', '오류', '주제 상세 정보를 불러오지 못했습니다.');
                setSelectedTopicId(null);
            }
        } catch (error) {
            console.error("Error fetching topic detail:", error);
            showAlert('error', '오류', '서버 통신 중 오류가 발생했습니다.');
            setSelectedTopicId(null);
        } finally {
            setIsTopicLoading(false);
        }
    };

    const handleReaction = async (topicId, reactionType) => {
        if (window.isReactionPending) return; // 연속 클릭 방지
        const token = localStorage.getItem("accessToken");
        if (!token) return;

        window.isReactionPending = true;
        try {
            const response = await fetch(`${API_BASE_URL}/projects/${projectId}/topics/${topicId}/reaction`, {
                method: 'POST',
                headers: { 
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    reaction: reactionType,
                    // 기존 데이터가 없는 상태(초기 생성)일 때는 무조건 null을 전달
                    version: topicDetail?.isReaction ? (topicDetail?.reactionVersion ?? null) : null
                })
            });

            if (response.ok) {
                const result = await response.json();
                // 전체를 재조회하지 않고 즉시 상태 업데이트 (반응 속도 개선 및 깜빡임 제거)
                setTopicDetail(prev => ({
                    ...prev,
                    isReaction: result.data.isReaction,
                    reactionVersion: result.data.reactionVersion
                }));
                // 목록도 갱신
                setRecommendations(prev => prev.map(t => 
                    t.topicId === topicId ? { ...t, isReaction: result.data.isReaction } : t
                ));
            } else if (response.status === 409) {
                const result = await response.json();
                showAlert('error', '충돌 발생', result.message || '다른 사용자가 먼저 반응을 변경했습니다.');
                fetchTopicDetail(topicId);
            } else {
                showAlert('error', '오류', '반응 처리에 실패했습니다.');
            }
        } catch (error) {
            console.error("Error handling reaction:", error);
            showAlert('error', '오류', '통신 중 오류가 발생했습니다.');
        } finally {
            window.isReactionPending = false;
        }
    };

    const handleBookmarkToggle = async (topicId) => {
        if (window.isBookmarkPending) return; // 연속 클릭 방지
        const token = localStorage.getItem("accessToken");
        if (!token) return;

        window.isBookmarkPending = true;
        try {
            const response = await fetch(`${API_BASE_URL}/projects/${projectId}/topics/${topicId}/bookmark`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (response.ok) {
                const result = await response.json();
                
                // 백엔드 API 응답 구조가 Boolean인지 Object인지 판별, 못 찾으면 기존 상태의 무조건 반대값 토글 적용
                let newStatus;
                if (typeof result.data === 'boolean') {
                    newStatus = result.data;
                } else if (result.data !== null && typeof result.data === 'object' && 'isBookmarked' in result.data) {
                    newStatus = result.data.isBookmarked;
                } else {
                    const currentTopic = recommendations.find(t => t.topicId === topicId) || topicDetail;
                    const isCurrentlyMarked = currentTopic?.isBookmarked === true || currentTopic?.isBookmarked === 'true' || currentTopic?.isBookmark === true;
                    newStatus = !isCurrentlyMarked;
                }
                
                // 목록 상태 즉시 업데이트
                setRecommendations(prev => prev.map(t => 
                    t.topicId === topicId ? { ...t, isBookmarked: newStatus } : t
                ));

                // 상세 보기 상태 즉시 업데이트
                if (selectedTopicId === topicId) {
                    setTopicDetail(prev => ({
                        ...prev,
                        isBookmarked: newStatus
                    }));
                }
            } else {
                showAlert('error', '오류', '북마크 처리에 실패했습니다.');
            }
        } catch (error) {
            console.error("Error handling bookmark:", error);
            showAlert('error', '오류', '통신 중 오류가 발생했습니다.');
        } finally {
            window.isBookmarkPending = false;
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

    const fetchUserProfile = async (userId) => {
        setIsUserLoading(true);
        const token = localStorage.getItem("accessToken");
        try {
            const response = await fetch(`${API_BASE_URL}/users/${userId}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const result = await response.json();
            if (response.ok && result.data) {
                setSelectedUser(result.data);
                setIsUserModalOpen(true);
            } else {
                showAlert('error', '죄송합니다', '사용자 프로필을 불러올 수 없습니다.');
            }
        } catch (error) {
            console.error("Error fetching user profile:", error);
            showAlert('error', '오류', '서버 통신 중 오류가 발생했습니다.');
        } finally {
            setIsUserLoading(false);
        }
    };

    if (loading) return <div className="loading">로딩 중...</div>;
    if (!project) return null;

    const isOwner = project.owner.userId === currentUserId;
    const getDomainName = (id) => DOMAINS.find(d => Number(d.id) === Number(id) || d.name === id || d.dbName === id)?.name || id;
    
    const getPositionObj = (id) => {
        if (!id) return null;
        // id가 객체로 넘어올 경우를 대비한 정제 로직
        const realId = (id && typeof id === 'object' && !Array.isArray(id)) 
            ? (id.id || id.positionId || id.position) 
            : id;
        
        if (!realId) return null;

        const numId = Number(realId);
        const found = POSITIONS.find(p => 
            p.id === numId || 
            String(p.id) === String(realId) ||
            (typeof realId === 'string' && (p.name === realId || p.dbName === realId))
        );
        
        if (!found) {
            console.warn(`Position mapping failed for ID:`, realId, "Raw Input:", id);
        }
        return found;
    };

    const getPositionName = (id) => getPositionObj(id)?.name || '기타';
    const getPositionIcon = (id) => getPositionObj(id)?.icon || '👤';

    const getSkillName = (id) => SKILLS.find(s => Number(s.id) === Number(id) || s.name === id)?.name || id;

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
                            <p className="project-description-summary">{project.description}</p>
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
                                        <div 
                                            key={member.userId} 
                                            className="member-small-card clickable"
                                            onClick={() => fetchUserProfile(member.userId)}
                                        >
                                            <span className="m-name">{member.nickname || member.name || '익명'}</span>
                                            <span className="m-pos">{getPositionName(member.positionId || member.position)}</span>
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
                            onClick={() => { setActiveTab('추천 주제'); setSelectedTopicId(null); setVisibleCount(6); }}
                        >
                            <MdAutoAwesome className="s-icon" /> 추천 주제
                        </div>
                        <div 
                            className={`sidebar-item ${activeTab === '주제 검색' ? 'active' : ''}`}
                            onClick={() => { setActiveTab('주제 검색'); setSelectedTopicId(null); setVisibleCount(6); }}
                        >
                            <MdSearch className="s-icon" /> 주제 검색
                        </div>
                        <div 
                            className={`sidebar-item ${activeTab === '북마크' ? 'active' : ''}`}
                            onClick={() => { setActiveTab('북마크'); setSelectedTopicId(null); setVisibleCount(6); }}
                        >
                            <MdBookmarkBorder className="s-icon" /> 북마크
                        </div>
                    </aside>

                    <section className="recommend-main">
                        {!selectedTopicId ? (
                            (() => {
                                // 북마크 여부 확인 유틸 함수
                                const isMarkedTopic = (t) => t.isBookmarked === true || t.isBookmarked === 'true' || t.isBookmark === true || t.isBookmark === 'true' || t.bookmarked === true || t.bookmarked === 'true';
                                
                                // 현재 탭 상태에 따라 보여줄 목록 필터링
                                const displayRecommendations = activeTab === '북마크' 
                                    ? recommendations.filter(isMarkedTopic)
                                    : recommendations;

                                return (
                                    <>
                                        <div className="recommend-header">
                                            <h2 className="recommend-title">{activeTab}</h2>
                                            <span className="recommend-count">
                                                {displayRecommendations.length > 0 
                                                    ? `${Math.min(visibleCount, displayRecommendations.length)} / ${displayRecommendations.length}` 
                                                    : '0 / 0'}
                                            </span>
                                        </div>

                                        {displayRecommendations.length === 0 ? (
                                            <div className="empty-state-message" style={{ textAlign: 'center', padding: '40px', color: '#888' }}>
                                                해당되는 주제가 없거나 북마크가 비어 있습니다.
                                            </div>
                                        ) : (
                                            <div className="topic-grid">
                                                {displayRecommendations.slice(0, visibleCount).map(topic => {
                                                    const isMarked = isMarkedTopic(topic);
                                                    
                                                    return (
                                                        <div 
                                                            key={topic.topicId} 
                                                            className="topic-card clickable"
                                                            onClick={() => setSelectedTopicId(topic.topicId)}
                                                        >
                                                            <div className="topic-card-header">
                                                                <h3 className="topic-title">{topic.title}</h3>
                                                                <div 
                                                                    className="bookmark-btn-wrap" 
                                                                    onClick={(e) => {
                                                                        e.stopPropagation();
                                                                        handleBookmarkToggle(topic.topicId);
                                                                    }}
                                                                >
                                                                    {isMarked ? (
                                                                        <MdBookmark className="bookmark-icon active" style={{ color: '#ee7c62' }} />
                                                                    ) : (
                                                                        <MdBookmarkBorder className="bookmark-icon" />
                                                                    )}
                                                                </div>
                                                            </div>
                                                            <div className="topic-domain-tag">{getDomainName(topic.domainId)}</div>
                                                            <div className="topic-footer">
                                                                <div className="topic-skills">
                                                                    {topic.skills.map(s => <span key={s} className="t-skill-tag">{getSkillName(s)}</span>)}
                                                                </div>
                                                            </div>
                                                        </div>
                                                    );
                                                })}
                                            </div>
                                        )}
                                        
                                        {displayRecommendations.length > visibleCount && (
                                            <div className="more-button-container">
                                                <button className="more-btn" onClick={() => setVisibleCount(displayRecommendations.length)}>
                                                    <MdAdd className="btn-icon" /> 더보기
                                                </button>
                                            </div>
                                        )}
                                    </>
                                );
                            })()
                        ) : (
                            <TopicDetailView 
                                topic={topicDetail} 
                                isLoading={isTopicLoading}
                                onBack={() => setSelectedTopicId(null)}
                                onReaction={handleReaction}
                                onBookmark={handleBookmarkToggle}
                                getDomainName={getDomainName}
                                getSkillName={getSkillName}
                            />
                        )}
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

                {/* 타 사용자 프로필 모달 */}
                {isUserModalOpen && selectedUser && (
                    <div className="modal-overlay" onClick={() => setIsUserModalOpen(false)}>
                        <div className="user-profile-modal" onClick={(e) => e.stopPropagation()}>
                            <div className="profile-header">
                                <div className="profile-title-wrap">
                                    <h2 className="profile-nickname">{selectedUser.nickname}</h2>
                                </div>
                                <button className="close-x-btn" onClick={() => setIsUserModalOpen(false)}>✕</button>
                            </div>
                            
                            <div className="profile-body">
                                {selectedUser.skillIds && selectedUser.skillIds.length > 0 && (
                                    <div className="profile-info-group">
                                        <p className="p-info-label">보유 기술 스택</p>
                                        <div className="p-skill-tags">
                                            {selectedUser.skillIds.map(id => (
                                                <span key={id} className="p-skill-tag">{getSkillName(id)}</span>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </div>
                            
                            <button className="profile-close-btn" onClick={() => setIsUserModalOpen(false)}>확인</button>
                        </div>
                    </div>
                )}

                {isUserLoading && (
                    <div className="modal-overlay">
                        <div className="loading-spinner-wrap">
                            <div className="loading-spinner"></div>
                            <p>프로필을 불러오는 중...</p>
                        </div>
                    </div>
                )}
            </main>
        </div>
    );
};

export default ProjectDetailPage;
