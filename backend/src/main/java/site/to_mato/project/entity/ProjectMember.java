package site.to_mato.project.entity;

import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import site.to_mato.common.entity.BaseEntity;
import site.to_mato.project.entity.enums.ProjectRole;
import site.to_mato.user.entity.User;

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

    @Builder(access = AccessLevel.PRIVATE)
    private ProjectMember(
            Project project,
            User user,
            ProjectRole role
    ) {
        this.project = project;
        this.user = user;
        this.projectRole = role;
    }

    public static ProjectMember ofOwner(Project project, User user) {
        return ProjectMember.builder()
                .project(project)
                .user(user)
                .role(ProjectRole.OWNER)
                .build();
    }

    public static ProjectMember ofMember(Project project, User user) {
        return ProjectMember.builder()
                .project(project)
                .user(user)
                .role(ProjectRole.MEMBER)
                .build();
    }

    public boolean isOwner() {
        return this.projectRole == ProjectRole.OWNER;
    }
}
