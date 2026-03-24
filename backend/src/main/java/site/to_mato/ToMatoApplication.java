package site.to_mato;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

@SpringBootApplication
@EnableScheduling
public class ToMatoApplication {

	public static void main(String[] args) {
		SpringApplication.run(ToMatoApplication.class, args);
	}

}
