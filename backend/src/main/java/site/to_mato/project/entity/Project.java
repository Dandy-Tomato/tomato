package site.to_mato.project.entity;

import java.time.LocalDateTime;

import lombok.AccessLevel;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.JdbcTypeCode;
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
    private LocalDateTime startedAt;

    @Column(name = "due_at")
    private LocalDateTime dueAt;

    @Column(name = "invite_code")
    private String inviteCode;

    @Column(name = "topic_state")
    private Boolean topicState;

    @Column(name = "last_processed_action_log_id")
    private Long lastProcessedActionLogId;

    @Column(name = "topic_embedding", columnDefinition = "vector(1536)")
    @JdbcTypeCode(SqlTypes.VECTOR)
    private float[] preferenceEmbeddings;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "owner_id", nullable = false)
    private User owner;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "confirmed_child_topic_id")
    private ChildTopic confirmedChildTopic;
}
