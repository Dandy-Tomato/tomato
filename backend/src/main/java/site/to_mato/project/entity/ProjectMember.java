package site.to_mato.project.entity;

import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.SQLDelete;
import org.hibernate.annotations.SQLRestriction;
import site.to_mato.common.entity.SoftDeleteEntity;
import site.to_mato.project.entity.enums.ProjectRole;
import site.to_mato.user.entity.User;

@Getter
@Entity
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@Table(
        name = "project_members",
        uniqueConstraints = {
                @UniqueConstraint(
                        name = "uk_project_member",
                        columnNames = {"project_id", "user_id"}
                )
        }
)
@SQLRestriction("deleted_at IS NULL")
@SQLDelete(sql = "UPDATE project_members SET deleted_at = CURRENT_TIMESTAMP WHERE project_member_id = ?")
public class ProjectMember extends SoftDeleteEntity {

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
