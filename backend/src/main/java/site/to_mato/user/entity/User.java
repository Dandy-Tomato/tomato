package site.to_mato.user.entity;

import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.SQLDelete;
import site.to_mato.common.entity.SoftDeleteEntity;

@Getter
@Entity
@Table(
        name = "users",
        uniqueConstraints = {
                @UniqueConstraint(columnNames = {"provider", "provider_id"})
        }
)
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@SQLDelete(sql = "UPDATE users SET deleted_at = CURRENT_TIMESTAMP WHERE user_id = ?")
public class User extends SoftDeleteEntity {

    @Id
    @Column(name = "user_id")
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(unique = true)
    private String email;

    private String password;

    private String nickname;

    @Column(name = "provider", length = 20)
    private String provider;

    @Column(name = "provider_id", length = 100)
    private String providerId;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private Role role;

    @Builder(access = AccessLevel.PRIVATE)
    private User(String email, String password, String nickname,
                 String provider, String providerId, Role role) {
        this.email = email;
        this.password = password;
        this.nickname = nickname;
        this.provider = provider;
        this.providerId = providerId;
        this.role = role;
    }

    // 일반 회원가입
    public static User createLocal(String email, String encodedPassword, String nickname) {
        return User.builder()
                .email(email)
                .password(encodedPassword)
                .nickname(nickname)
                .provider("local")
                .providerId(email)
                .role(Role.ROLE_USER)
                .build();
    }

    // OAuth 회원가입
    public static User createOAuth(String provider, String providerId,
                                   String nickname, String email) {
        return User.builder()
                .email(email)
                .password(null)
                .nickname(nickname)
                .provider(provider)
                .providerId(providerId)
                .role(Role.ROLE_USER)
                .build();
    }
}