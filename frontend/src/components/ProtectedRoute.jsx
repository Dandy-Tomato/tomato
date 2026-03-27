import React from 'react';
import { Navigate } from 'react-router-dom';

/**
 * 인증된 사용자만 접근할 수 있도록 보호하는 라우트 컴포넌트
 * accessToken이 없으면 로그인 페이지(/)로 리다이렉트합니다.
 */
const ProtectedRoute = ({ children }) => {
    const accessToken = localStorage.getItem('accessToken');

    if (!accessToken) {
        // 인증되지 않은 사용자는 로그인 페이지로 리다이렉트
        return <Navigate to="/" replace />;
    }

    // 인증된 사용자는 요청한 컴포넌트 렌더링
    return children;
};

export default ProtectedRoute;
