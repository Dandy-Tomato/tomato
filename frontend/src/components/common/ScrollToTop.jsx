import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';

/**
 * 페이지(라우트 경로)가 변경될 때마다 화면 스크롤을 항상
 * 최상단(0, 0)으로 이동시켜주는 편의용 컴포넌트입니다.
 */
const ScrollToTop = () => {
    // 현재 URL의 path 정보를 가져옵니다.
    const { pathname } = useLocation();

    // pathname이 변경될 때마다(즉, 다른 페이지로 이동할 때마다) 실행됩니다.
    useEffect(() => {
        window.scrollTo(0, 0); // 스크롤을 맨 위로 설정
    }, [pathname]);

    // 화면에 직접 렌더링할 시각적인 DOM 요소는 필요없으므로 null을 반환합니다.
    return null;
};

export default ScrollToTop;
