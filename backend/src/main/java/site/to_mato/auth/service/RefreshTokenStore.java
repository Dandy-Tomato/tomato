package site.to_mato.auth.service;

import lombok.RequiredArgsConstructor;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;
import site.to_mato.common.security.jwt.JwtProperties;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

@Service
@RequiredArgsConstructor
public class RefreshTokenStore {

    private final JwtProperties jwtProperties;
    private final StringRedisTemplate redisTemplate;

    private static final String KEY_PREFIX = "rt:";

    public void save(String refreshRaw, Long userId) {
        redisTemplate.opsForValue().set(
                key(refreshRaw),
                String.valueOf(userId),
                jwtProperties.refreshTokenTtl()
        );
    }

    public Long findUserId(String refreshRaw) {
        String key = key(refreshRaw);
        String val = redisTemplate.opsForValue().get(key);
        return (val == null) ? null : Long.valueOf(val);
    }

    public void delete(String refreshRaw) {
        redisTemplate.delete(key(refreshRaw));
    }

    public void rotate(String oldRefreshRaw, String newRefreshRaw, Long userId) {
        save(newRefreshRaw, userId);
        delete(oldRefreshRaw);
    }

    private String key(String refreshRaw) {
        return KEY_PREFIX + sha256(refreshRaw);
    }

    public static String sha256(String raw) {
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            byte[] digest = md.digest(raw.getBytes(StandardCharsets.UTF_8));
            return toHex(digest);
        } catch (NoSuchAlgorithmException e) {
            throw new IllegalStateException("SHA-256 not available", e);
        }
    }

    private static String toHex(byte[] bytes) {
        StringBuilder sb = new StringBuilder(bytes.length * 2);
        for (byte b : bytes) sb.append(String.format("%02x", b));
        return sb.toString();
    }
}