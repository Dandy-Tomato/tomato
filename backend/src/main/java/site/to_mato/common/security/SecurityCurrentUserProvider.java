package site.to_mato.common.security;

import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import site.to_mato.common.exception.CustomException;
import site.to_mato.common.exception.ErrorCode;

@Component
public class SecurityCurrentUserProvider implements CurrentUserProvider {

    @Override
    public Long getCurrentUserId() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();

        if (authentication == null || !authentication.isAuthenticated()) {
            throw new CustomException(ErrorCode.UNAUTHORIZED);
        }

        String principal = authentication.getName();
        if (principal == null || principal.isBlank() || "anonymousUser".equals(principal)) {
            throw new CustomException(ErrorCode.UNAUTHORIZED);
        }

        try {
            return Long.parseLong(principal);
        } catch (NumberFormatException e) {
            throw new CustomException(ErrorCode.UNAUTHORIZED);
        }
    }
}