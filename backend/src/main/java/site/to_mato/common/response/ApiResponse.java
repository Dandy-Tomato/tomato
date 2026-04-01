package site.to_mato.common.response;

import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.AccessLevel;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import org.springframework.http.HttpStatus;
import site.to_mato.common.exception.ErrorCode;

@Getter
@AllArgsConstructor(access = AccessLevel.PRIVATE)
@Builder(access = AccessLevel.PRIVATE)
@JsonInclude(JsonInclude.Include.NON_NULL)
public class ApiResponse<T> {

    private final int statusCode;
    private final String message;
    private final Integer errorCode;
    private final T data;

    public static <T> ApiResponse<T> ok(T data) {
        return ApiResponse.<T>builder()
                .statusCode(HttpStatus.OK.value())
                .message("OK")
                .data(data)
                .build();
    }

    public static ApiResponse<Void> error(ErrorCode errorCode) {
        return ApiResponse.<Void>builder()
                .statusCode(errorCode.getStatus().value())
                .message(errorCode.getMessage())
                .errorCode(errorCode.getCode())
                .build();
    }

    public static ApiResponse<Void> error(HttpStatus status, String message) {
        return ApiResponse.<Void>builder()
                .statusCode(status.value())
                .message(message)
                .build();
    }
}
