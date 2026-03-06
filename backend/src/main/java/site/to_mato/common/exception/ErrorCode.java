package site.to_mato.common.exception;

import lombok.Getter;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;

@Getter
@RequiredArgsConstructor
public enum ErrorCode {

    // =========================
    // 1000: COMMON
    // =========================
    INVALID_REQUEST(HttpStatus.BAD_REQUEST, 1000, "잘못된 요청입니다."),
    VALIDATION_ERROR(HttpStatus.BAD_REQUEST, 1001, "입력값이 올바르지 않습니다."),

    // =========================
    // 2000: AUTH
    // =========================
    UNAUTHORIZED(HttpStatus.UNAUTHORIZED, 2000, "인증이 필요합니다."),
    FORBIDDEN(HttpStatus.FORBIDDEN, 2001, "접근 권한이 없습니다."),
    TOKEN_EXPIRED(HttpStatus.UNAUTHORIZED, 2002, "토큰이 만료되었습니다."),
    INVALID_CREDENTIALS(HttpStatus.UNAUTHORIZED, 2003, "이메일 또는 비밀번호가 올바르지 않습니다."),
    REFRESH_TOKEN_INVALID(HttpStatus.UNAUTHORIZED, 2004, "리프레시 토큰이 유효하지 않습니다."),
    REFRESH_TOKEN_REVOKED(HttpStatus.UNAUTHORIZED, 2005, "리프레시 토큰이 만료되었거나 폐기되었습니다."),
    OAUTH_ONLY_ACCOUNT(HttpStatus.BAD_REQUEST, 2006, "소셜 로그인 계정입니다. 소셜 로그인을 이용해주세요."),
    OAUTH_PROVIDER_NOT_SUPPORTED(HttpStatus.BAD_REQUEST, 2007, "지원하지 않는 OAuth Provider입니다."),

    // =========================
    // 3000: USER
    // =========================
    USER_NOT_FOUND(HttpStatus.NOT_FOUND, 3000, "존재하지 않는 사용자입니다."),
    DUPLICATE_USER(HttpStatus.CONFLICT, 3001, "이미 존재하는 사용자입니다."),
    POSITION_NOT_FOUND(HttpStatus.NOT_FOUND, 3002, "존재하지 않는 직무입니다."),

    // =========================
    // 4000: TEAM
    // =========================
    TEAM_NOT_FOUND(HttpStatus.NOT_FOUND, 4000, "존재하지 않는 팀입니다."),
    TEAM_FULL(HttpStatus.BAD_REQUEST, 4001, "팀 인원이 가득 찼습니다."),

    // =========================
    // 5000: RECOMMENDATION
    // =========================
    RECOMMENDATION_FAILED(HttpStatus.INTERNAL_SERVER_ERROR, 5000, "추천 생성에 실패했습니다."),

    // =========================
    // 9000: SERVER
    // =========================
    INTERNAL_SERVER_ERROR(HttpStatus.INTERNAL_SERVER_ERROR, 9000, "서버 오류가 발생했습니다.");

    private final HttpStatus status;
    private final int code;
    private final String message;
}