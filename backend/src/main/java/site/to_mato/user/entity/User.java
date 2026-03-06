package site.to_mato.user.entity;

import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.SQLDelete;
import site.to_mato.catalog.entity.Position;
import site.to_mato.common.entity.SoftDeleteEntity;
import site.to_mato.user.entity.enums.Role;

@Getter
@Entity
@Table(name = "users")
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@SQLDelete(sql = "UPDATE users SET deleted_at = CURRENT_TIMESTAMP WHERE user_id = ?")
public class User extends SoftDeleteEntity {

    @Id
    @Column(name = "user_id")
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(unique = true, length = 255)
    private String email;

    @Column(length = 255)
    private String password;

    @Column(length = 50)
    private String nickname;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    private Role role;

    @Column(name = "is_onboarding", nullable = false)
    private boolean isOnboarding;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "position_id")
    private Position position;

    @Builder(access = AccessLevel.PRIVATE)
    private User(String email, String password, String nickname,
                 Role role, boolean isOnboarding, Position position) {
        this.email = email;
        this.password = password;
        this.nickname = nickname;
        this.role = role;
        this.isOnboarding = isOnboarding;
        this.position = position;
    }

    // 일반 회원가입
    public static User createLocal(String email, String encodedPassword, String nickname, Position position) {
        return User.builder()
                .email(email)
                .password(encodedPassword)
                .nickname(nickname)
                .role(Role.ROLE_USER)
                .isOnboarding(true)
                .position(position)
                .build();
    }

    // OAuth 회원가입
    public static User createOAuth(String email) {
        return User.builder()
                .email(email)
                .password(null)
                .nickname(null)
                .role(Role.ROLE_USER)
                .isOnboarding(false)
                .position(null)
                .build();
    }

    // 온보딩 완료
    public void completeOnboarding(String nickname, Position position) {
        this.nickname = nickname;
        this.position = position;
        this.isOnboarding = true;
    }
}