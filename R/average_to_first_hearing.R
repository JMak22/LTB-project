df <- readr::read_csv(here::here("cleaned_data/Avg_Days_First_Hearing", "LTBAvgDayFirstHearing_all_quarters.csv"))
library(tidyverse)
colnames(df)

df |> 
  distinct(report_id) |> 
  print(n = Inf)


df |> mutate(
  # start_date = substr(source_file, 6, 15) |> as_date(),
  # end_date = substr(source_file, 17, 25) |>  as_date()
) |> 
  # select(report_id, 
  #   # start_date, end_date, 
  #   source_file, avg_days) |> 
  mutate(
    # period = lubridate::interval(start = start_date, end = end_date)
  ) |> 
  summarise(.by = c(report_id,region_id), avg = median(avg_days)) |> 
  ggplot()+
  labs(
    title = "Average days to first LTB hearing", 
    subtitle = "per quarter 2016-2025",
    x = "quarter", y = "days")+
  aes(x = (as.factor(report_id)), y = avg, group = 1)+
  geom_line()+
  geom_smooth(method = "lm", se = FALSE)+
  scale_y_continuous(limits = c(0, 365))+
  facet_wrap(~region_id)+
  theme(
    axis.text.x.bottom = element_text(angle = 90)
  )

