import React from 'react';
import { MdCheckCircle, MdError, MdInfo } from 'react-icons/md';

const AlertModal = ({ isOpen, type = 'success', title, message, onClose, onConfirm, showCancel = false }) => {
    if (!isOpen) return null;

    const getIcon = () => {
        switch (type) {
            case 'error': return <MdError size={32} />;
            case 'info': return <MdInfo size={32} />;
            default: return <MdCheckCircle size={32} />;
        }
    };

    return (
        <div className="common-modal-overlay" onClick={onClose}>
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
                            if (onConfirm) onConfirm();
                            onClose();
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
