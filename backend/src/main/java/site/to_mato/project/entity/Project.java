package site.to_mato.project.entity;

import java.time.LocalDateTime;
import java.util.List;

import site.to_mato.common.entity.SoftDeleteEntity;
import site.to_mato.user.entity.User;
import site.to_mato.topic.entity.ChildTopic;

import jakarta.persistence.*;
import lombok.Getter;

@Getter
@Entity
@Table(name = "projects")
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

    @Column(name = "preference_embeddings")
    private List<Float> preferenceEmbeddings;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "owner_id", nullable = false)
    private User ownerId;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "confirmed_child_topic_id", nullable = true)
    private ChildTopic confirmedChildTopicId;
}
