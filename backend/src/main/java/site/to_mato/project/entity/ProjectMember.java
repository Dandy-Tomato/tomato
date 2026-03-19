package site.to_mato.project.entity;

import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import site.to_mato.common.entity.BaseEntity;
import site.to_mato.user.entity.User;

import java.time.LocalDateTime;

@Getter
@Entity
@Table(name = "project_members")
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class ProjectMember extends BaseEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "project_member_id")
    private Long id;

    @Enumerated(EnumType.STRING)
    @Column(name = "project_role", nullable = false)
    private ProjectRole projectRole;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "project_id", nullable = false)
    private Project project;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    @Builder
    private ProjectMember(
            ProjectRole projectRole,
            Project project,
            User user
    ) {
        this.projectRole = projectRole;
        this.project = project;
        this.user = user;
    }

    public static ProjectMember of(
            Project project,
            User user,
            ProjectRole projectRole
    ) {
        LocalDateTime now = LocalDateTime.now();

        return ProjectMember.builder()
                .project(project)
                .user(user)
                .projectRole(projectRole)
                .build();
    }

    public void changeRole(ProjectRole projectRole) {
        this.projectRole = projectRole;
    }
}
