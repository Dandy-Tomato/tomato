package site.to_mato.project.entity;

import java.time.LocalDate;

import lombok.AccessLevel;
import lombok.Builder;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.annotations.SQLDelete;
import org.hibernate.annotations.SQLRestriction;
import org.hibernate.type.SqlTypes;
import site.to_mato.common.entity.SoftDeleteEntity;
import site.to_mato.user.entity.User;
import site.to_mato.topic.entity.ChildTopic;

import jakarta.persistence.*;
import lombok.Getter;

@Getter
@Entity
@Table(name = "projects")
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@SQLRestriction("deleted_at IS NULL")
@SQLDelete(sql = "UPDATE projects SET deleted_at = CURRENT_TIMESTAMP WHERE project_id = ?")
public class Project extends SoftDeleteEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "project_id")
    private Long id;

    @Column(name = "name")
    private String name;

    @Column(name = "description")
    private String description;

    @Column(name = "started_at")
    private LocalDate startedAt;

    @Column(name = "due_at")
    private LocalDate dueAt;

    @Column(name = "invite_code", unique = true)
    private String inviteCode;

    @Column(name = "topic_state")
    private Boolean topicState;

    @Column(name = "last_processed_action_log_id")
    private Long lastProcessedActionLogId;

    @Column(name = "preference_embedding", columnDefinition = "vector(1536)")
    @JdbcTypeCode(SqlTypes.VECTOR)
    @Transient
    private float[] preferenceEmbedding;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "owner_id", nullable = false)
    private User owner;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "confirmed_child_topic_id")
    private ChildTopic confirmedChildTopic;

    @Builder(access = AccessLevel.PRIVATE)
    private Project(
            User owner,
            String name,
            String description,
            LocalDate startedAt,
            LocalDate dueAt,
            String inviteCode,
            boolean topicState
    ) {
        this.owner = owner;
        this.name = name;
        this.description = description;
        this.startedAt = startedAt;
        this.dueAt = dueAt;
        this.inviteCode = inviteCode;
        this.topicState = topicState;
    }

    public static Project create(
            User owner,
            String name,
            String description,
            LocalDate startedAt,
            LocalDate dueAt,
            String inviteCode
    ) {
        return Project.builder()
                .owner(owner)
                .name(name)
                .description(description)
                .startedAt(startedAt)
                .dueAt(dueAt)
                .inviteCode(inviteCode)
                .topicState(false)
                .build();
    }

    public void update(String name, String description, LocalDate startedAt, LocalDate dueAt) {
        this.name = name;
        this.description = description;
        this.startedAt = startedAt;
        this.dueAt = dueAt;
    }

    public void confirmTopic(ChildTopic childTopic) {
        this.topicState = true;
        this.confirmedChildTopic = childTopic;
    }

    public void clearConfirmedTopic() {
        this.topicState = false;
        this.confirmedChildTopic = null;
    }
}
