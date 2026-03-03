package site.to_mato.common.security.jwt;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.JwtException;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import jakarta.annotation.PostConstruct;
import jakarta.servlet.http.HttpServletRequest;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.Date;
import java.util.List;
import javax.crypto.SecretKey;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.stereotype.Component;

@Component
public class JwtTokenProvider {

    private final JwtProperties props;
    private SecretKey key;

    public JwtTokenProvider(JwtProperties props) {
        this.props = props;
    }

    @PostConstruct
    void initKey() {
        this.key = Keys.hmacShaKeyFor(props.secret().getBytes(StandardCharsets.UTF_8));
    }

    public String createAccessToken(Long userId, String role) {
        Instant now = Instant.now();
        Instant exp = now.plus(props.accessTokenTtl());

        return Jwts.builder()
                .subject(String.valueOf(userId))
                .claim("role", role)
                .issuedAt(Date.from(now))
                .expiration(Date.from(exp))
                .signWith(key)
                .compact();
    }

    public String createRefreshToken(Long userId) {
        Instant now = Instant.now();
        Instant exp = now.plus(props.refreshTokenTtl());

        return Jwts.builder()
                .subject(String.valueOf(userId))
                .issuedAt(Date.from(now))
                .expiration(Date.from(exp))
                .signWith(key)
                .compact();
    }

    public boolean validateToken(String token) {
        try {
            parseClaims(token);
            return true;
        } catch (JwtException | IllegalArgumentException e) {
            return false;
        }
    }

    public Authentication getAuthentication(String token) {
        Claims claims = parseClaims(token);

        Long userId = Long.valueOf(claims.getSubject());
        String role = claims.get("role", String.class);

        List<SimpleGrantedAuthority> authorities =
                (role == null || role.isBlank())
                        ? List.of()
                        : List.of(new SimpleGrantedAuthority(role));

        return new UsernamePasswordAuthenticationToken(userId, null, authorities);
    }

    public String resolveToken(HttpServletRequest request) {
        String headerName = props.header();
        String rawHeaderValue = request.getHeader(headerName);
        if (rawHeaderValue == null) return null;

        String prefix = props.prefix();
        if (prefix == null || prefix.isBlank()) return null;

        if (!rawHeaderValue.startsWith(prefix)) return null;

        return rawHeaderValue.substring(prefix.length()).trim();
    }

    public Long getUserId(String token) {
        Claims claims = parseClaims(token);
        return Long.valueOf(claims.getSubject());
    }

    public Instant getExpiryInstant(String token) {
        Claims claims = parseClaims(token);
        Date exp = claims.getExpiration();
        return exp.toInstant();
    }

    private Claims parseClaims(String token) {
        return Jwts.parser()
                .verifyWith(key)
                .build()
                .parseSignedClaims(token)
                .getPayload();
    }
}