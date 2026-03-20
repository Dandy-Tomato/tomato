package site.to_mato.project.dto;

import java.time.LocalDateTime;
import java.util.List;

public final class ProjectResponseDto {

    private ProjectResponseDto() {
    }

    public record OwnerSummary(
            Long userId,
            String nickname
    ) {
    }

    public record DomainItem(
            Long domainId,
            String name
    ) {
    }

    public record ProjectDomainItem(
            Long projectDomainId,
            Long domainId,
            String name
    ) {
    }

    public record ProjectSkillItem(
            Long projectSkillId,
            Long skillId,
            String name,
            long weight
    ) {
    }

    public record PositionSummary(
            Long positionId,
            String name
    ) {
    }

    public record ProjectMemberItem(
            Long projectMemberId,
            Long userId,
            String nickname,
            String githubUsername,
            String projectRole,
            PositionSummary position,
            LocalDateTime joinedAt
    ) {
    }

    public record MyProjectItem(
            Long projectId,
            String name,
            String description,
            String projectRole,
            boolean topicState,
            long memberCount,
            LocalDateTime startedAt,
            LocalDateTime dueAt,
            LocalDateTime createdAt
    ) {
    }

    public record CreateData(
            Long projectId,
            String name,
            String description,
            LocalDateTime startedAt,
            LocalDateTime dueAt,
            String inviteCode,
            boolean topicState,
            OwnerSummary owner,
            List<DomainItem> domains,
            LocalDateTime createdAt
    ) {
    }

    public record DetailData(
            Long projectId,
            String name,
            String description,
            LocalDateTime startedAt,
            LocalDateTime dueAt,
            String inviteCode,
            boolean topicState,
            Long confirmedChildTopicId,
            OwnerSummary owner,
            List<DomainItem> domains,
            List<ProjectSkillItem> skills,
            long memberCount,
            LocalDateTime createdAt,
            LocalDateTime updatedAt
    ) {
    }

    public record UpdateData(
            Long projectId,
            String name,
            String description,
            LocalDateTime startedAt,
            LocalDateTime dueAt,
            List<DomainItem> domains,
            LocalDateTime updatedAt
    ) {
    }

    public record DeleteData(
            Long projectId,
            LocalDateTime deletedAt
    ) {
    }

    public record TopicConfirmationData(
            Long projectId,
            boolean topicState,
            Long confirmedChildTopicId,
            LocalDateTime updatedAt
    ) {
    }

    public record InviteLookupData(
            Long projectId,
            String projectName,
            String ownerNickname,
            boolean alreadyJoined
    ) {
    }

    public record JoinData(
            Long projectId,
            String projectName,
            String projectRole,
            LocalDateTime joinedAt
    ) {
    }

    public record LeaveData(
            Long projectId,
            Long userId,
            LocalDateTime leftAt
    ) {
    }

    public record TransferOwnerData(
            Long projectId,
            Long previousOwnerUserId,
            Long newOwnerUserId,
            LocalDateTime updatedAt
    ) {
    }
}