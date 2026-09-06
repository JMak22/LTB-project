staffing_metrics <- function() {
  library(readr)
  library(dplyr)

  df <- read_csv(here::here("cleaned_data", "staffing_metrics.csv"))

  glimpse(df)

  df |>
    ggplot() +
    aes(x = value, y = report_id) +
    geom_col() +
    facet_wrap(~metric_id) +
    theme_minimal()
}
# staffing_metrics()
