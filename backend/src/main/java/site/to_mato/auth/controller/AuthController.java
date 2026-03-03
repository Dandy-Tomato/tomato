package site.to_mato.auth.controller;

import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
import site.to_mato.auth.dto.request.RefreshRequest;
import site.to_mato.auth.dto.response.TokenResponse;
import site.to_mato.auth.service.AuthService;
import site.to_mato.common.response.ApiResponse;

@RestController
@RequiredArgsConstructor
@RequestMapping("/auth")
public class AuthController {

    private final AuthService authService;

    @PostMapping("/refresh")
    public ApiResponse<TokenResponse> refresh(@RequestBody @Valid RefreshRequest req) {
        return ApiResponse.ok(authService.refresh(req.refreshToken()));
    }
}