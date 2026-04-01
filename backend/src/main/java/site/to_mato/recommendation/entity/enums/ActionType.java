package site.to_mato.recommendation.entity.enums;

public enum ActionType {
    IMPRESSION,         // 추천 목록에 노출
    VIEW_DETAIL,        // 상세 조회
    VIEW_SPECIFICATION, // 구체화 조회

    LIKE,               // 좋아요
    LIKE_CANCEL,

    DISLIKE,            // 싫어요
    DISLIKE_CANCEL,

    BOOKMARK,           // 북마크
    BOOKMARK_CANCEL
}
