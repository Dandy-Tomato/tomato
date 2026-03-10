package site.to_mato.recommendation.entity;

import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import site.to_mato.common.entity.BaseEntity;
import site.to_mato.recommendation.entity.enums.ActionLogProcessStatus;

import java.time.LocalDateTime;

@Getter
@Entity
@Table(name = "action_log_processes")
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class ActionLogProcess extends BaseEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "action_log_process_id")
    private Long id;

    @Enumerated(EnumType.STRING)
    @Column(name = "status", nullable = false, length = 20)
    private ActionLogProcessStatus status;

    @Column(name = "retry_count", nullable = false)
    private Integer retryCount;

    @Column(name = "started_at")
    private LocalDateTime startedAt;

    @Column(name = "completed_at")
    private LocalDateTime completedAt;

    @Column(name = "error_message")
    private String errorMessage;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "action_log_id", nullable = false, unique = true)
    private ActionLog actionLog;

    @Builder
    private ActionLogProcess(
            ActionLog actionLog,
            ActionLogProcessStatus status,
            Integer retryCount,
            LocalDateTime startedAt,
            LocalDateTime completedAt,
            String errorMessage
    ) {
        this.actionLog = actionLog;
        this.status = status;
        this.retryCount = retryCount;
        this.startedAt = startedAt;
        this.completedAt = completedAt;
        this.errorMessage = errorMessage;
    }

    public static ActionLogProcess pending(ActionLog actionLog) {
        return ActionLogProcess.builder()
                .actionLog(actionLog)
                .status(ActionLogProcessStatus.PENDING)
                .retryCount(0)
                .build();
    }

    public void markProcessing() {
        LocalDateTime now = LocalDateTime.now();
        this.status = ActionLogProcessStatus.PROCESSING;
        if (this.startedAt == null) {
            this.startedAt = now;
        }
    }

    public void markSuccess() {
        LocalDateTime now = LocalDateTime.now();
        this.status = ActionLogProcessStatus.SUCCESS;
        if (this.startedAt == null) {
            this.startedAt = now;
        }
        this.completedAt = now;
        this.errorMessage = null;
    }

    public void markFailed(String errorMessage) {
        LocalDateTime now = LocalDateTime.now();
        this.status = ActionLogProcessStatus.FAILED;
        if (this.startedAt == null) {
            this.startedAt = now;
        }
        this.completedAt = now;
        this.errorMessage = errorMessage;
    }

    public void increaseRetryCount() {
        this.retryCount++;
    }
}
