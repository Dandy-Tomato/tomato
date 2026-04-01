import React from 'react';
import { MdCheckCircle, MdError, MdInfo } from 'react-icons/md';

/**
 * 전역적이고 재사용 가능한 알림(Alert) 모달 컴포넌트
 * 커스텀 UI를 제공하며, 브라우저 기본 내장 alert()을 대신합니다.
 * 
 * @param {boolean} isOpen 모달의 노출 여부
 * @param {string} type 모달 애니메이션 및 아이콘 타입 ('success' | 'error' | 'info')
 * @param {string} title 모달창 상단 제목 노출
 * @param {string} message 사용자에게 보여줄 안내 메시지
 * @param {function} onClose 모달 닫기 버튼 핸들러
 * @param {function} onConfirm '확인'을 눌렀을 때 실행할 콜백 체인 동작
 * @param {boolean} showCancel 취소 버튼 노출 여부 지정 (기본값 false)
 */
const AlertModal = ({ isOpen, type = 'success', title, message, onClose, onConfirm, showCancel = false }) => {
    // 렌더링을 방지하기 위해 열려있지 않을 땐 null 반환
    if (!isOpen) return null;

    // 타입에 따른 아이콘을 동적으로 가져옵니다.
    const getIcon = () => {
        switch (type) {
            case 'error': return <MdError size={32} />;
            case 'info': return <MdInfo size={32} />;
            default: return <MdCheckCircle size={32} />;
        }
    };

    return (
        // 바깥 어두운 배경 클릭 시 알림창 닫음 처리
        <div className="common-modal-overlay" onClick={onClose}>
            {/* 이벤트 버블링을 막아 모달 내부를 눌렀을 때 닫히지 않도록 막음 */}
            <div className="common-alert-modal" onClick={(e) => e.stopPropagation()}>
                
                <div className={`common-modal-icon-wrap ${type}`}>
                    {getIcon()}
                </div>
                
                <h2 className="common-modal-title">{title}</h2>
                <p className="common-modal-desc">{message}</p>
                
                <div className="common-modal-footer" style={{ display: 'flex', gap: '12px', width: '100%' }}>
                    {showCancel && (
                        <button className="common-modal-btn cancel" onClick={onClose} style={{ backgroundColor: '#f5f5f5', color: '#777' }}>
                            취소
                        </button>
                    )}
                    
                    <button 
                        className={`common-modal-btn ${type}`} 
                        onClick={() => {
                            if (onConfirm) onConfirm(); // 콜백 실행
                            onClose(); // 처리가 끝난 뒤 모달 닫기
                        }}
                        autoFocus
                    >
                        확인
                    </button>
                </div>
                
            </div>
        </div>
    );
};

export default AlertModal;
