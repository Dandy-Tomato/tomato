import React from 'react';
import { Navigate } from 'react-router-dom';

/**
 * 인증된 사용자만 접근할 수 있도록 보호해 주는 라우트 래퍼 컴포넌트입니다.
 * 로컬 스토리지에 accessToken이 없으면 즉시 로그인 페이지(/)로 리다이렉트합니다.
 * 
 * @param {children} ReactNode - 보호해야 하는 하위 자식 컴포넌트 
 */
const ProtectedRoute = ({ children }) => {
    // 로컬 스토리지에서 액세스 토큰 존재 여부를 확인합니다.
    const accessToken = localStorage.getItem('accessToken');

    if (!accessToken) {
        // 인증되지 않은 사용자(토큰이 없는 사용자)는 로그인 페이지(루트 주소)로 리다이렉트
        return <Navigate to="/" replace />;
    }

    // 정상적으로 인증된 사용자라면, 요청한 원래 컴포넌트를 렌더링합니다.
    return children;
};

export default ProtectedRoute;
