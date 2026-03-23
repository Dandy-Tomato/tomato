package site.to_mato.recommendation.entity;

import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import site.to_mato.recommendation.entity.enums.ActionType;

import java.time.LocalDateTime;

@Getter
@Entity
@Table(name = "action_logs")
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class ActionLog {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "action_log_id")
    private Long id;

    @Column(name = "actor_user_id", nullable = false)
    private Long actorUserId;

    @Column(name = "project_id", nullable = false)
    private Long projectId;

    @Column(name = "topic_id", nullable = false)
    private Long topicId;

    @Enumerated(EnumType.STRING)
    @Column(name = "action_type", nullable = false, length = 30)
    private ActionType actionType;

    @Column(name = "created_at", nullable = false)
    private LocalDateTime createdAt;

    @Lob
    @Column(name = "meta")
    private String meta;

    @Builder(access = AccessLevel.PRIVATE)
    private ActionLog(
            Long actorUserId,
            Long projectId,
            Long topicId,
            ActionType actionType,
            LocalDateTime createdAt,
            String meta
    ) {
        this.actorUserId = actorUserId;
        this.projectId = projectId;
        this.topicId = topicId;
        this.actionType = actionType;
        this.createdAt = createdAt;
        this.meta = meta;
    }

    public static ActionLog of(
            Long actorUserId,
            Long projectId,
            Long topicId,
            ActionType actionType,
            String meta
    ) {
        return ActionLog.builder()
                .actorUserId(actorUserId)
                .projectId(projectId)
                .topicId(topicId)
                .actionType(actionType)
                .createdAt(LocalDateTime.now())
                .meta(meta)
                .build();
    }
}
