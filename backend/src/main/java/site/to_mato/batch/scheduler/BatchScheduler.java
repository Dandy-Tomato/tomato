package site.to_mato.batch.scheduler;

import lombok.RequiredArgsConstructor;
import org.springframework.batch.core.Job;
import org.springframework.batch.core.JobParameters;
import org.springframework.batch.core.JobParametersBuilder;
import org.springframework.batch.core.launch.JobLauncher;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import java.time.LocalDate;
import java.time.format.DateTimeFormatter;

@Component
@RequiredArgsConstructor
public class BatchScheduler {

    private final JobLauncher jobLauncher;
    private final Job companyImportJob;

    // cron: 초 분 시간 일 월 요일 (*: 매 시간)
    @Scheduled(cron = "${batch.scheduler.company-cron}")
    public void runJob() throws Exception {
        String date = LocalDate.now().format(DateTimeFormatter.ofPattern("yyMMdd"));

        JobParameters params = new JobParametersBuilder()
                .addString("date", date)
                .addLong("time", System.currentTimeMillis())
                .toJobParameters();

        jobLauncher.run(companyImportJob, params);
    }

}
