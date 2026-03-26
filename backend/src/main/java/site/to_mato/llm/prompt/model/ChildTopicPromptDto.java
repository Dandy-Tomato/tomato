package site.to_mato.llm.prompt.model;

import site.to_mato.project.entity.Project;
import site.to_mato.topic.entity.Topic;

import java.time.temporal.ChronoUnit;
import java.util.List;

public record ChildTopicPromptDto(
        TeamInfo team,
        TopicInfo topic
) {

    public record TeamInfo(
            int memberCount,
            List<String> skills,
            List<String> domains,
            long durationWeeks
    ) {}

    public record TopicInfo(
            String title,
            String description,
            int difficulty,
            int recommendedTeamSize,
            int expectedDurationWeek
    ) {}

    public static ChildTopicPromptDto of(
            Project project,
            Topic topic,
            int memberCount,
            List<String> skills,
            List<String> domains
    ) {
        long durationWeeks = calculateDuration(project);

        return new ChildTopicPromptDto(
                new TeamInfo(
                        memberCount == 0 ? 1 : memberCount,
                        skills,
                        domains,
                        durationWeeks
                ),
                new TopicInfo(
                        topic.getTitle(),
                        topic.getDescription(),
                        topic.getDifficulty(),
                        topic.getRecommendedTeamSize(),
                        topic.getExpectedDurationWeek()
                )
        );
    }

    private static long calculateDuration(Project project) {
        if (project.getStartedAt() == null || project.getDueAt() == null) {
            return 0;
        }
        return ChronoUnit.WEEKS.between(
                project.getStartedAt(),
                project.getDueAt()
        );
    }
}
