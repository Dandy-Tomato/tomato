package site.to_mato.user.controller;

import lombok.RequiredArgsConstructor;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;
import site.to_mato.common.response.ApiResponse;
import site.to_mato.user.dto.response.MyProfileResponse;
import site.to_mato.user.dto.response.UserProfileResponse;
import site.to_mato.user.service.UserService;

@RestController
@RequiredArgsConstructor
@RequestMapping("/users")
public class UserController {

    private final UserService userService;

    @GetMapping("/profile")
    public ApiResponse<MyProfileResponse> getMyProfile(
            @AuthenticationPrincipal Long userId
    ) {
        return ApiResponse.ok(userService.getMyProfile(userId));
    }

    @GetMapping("/{userId}")
    public ApiResponse<UserProfileResponse> getUserProfile(
            @PathVariable Long userId
    ) {
        return ApiResponse.ok(userService.getUserProfile(userId));
    }
}
