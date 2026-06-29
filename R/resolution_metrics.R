resolution_metrics <- function() {
  library(readr)
  library(dplyr)
  library(tidyr)
  library(ggplot2)

  df <- read_csv(here::here("cleaned_data", "resolution_metrics.csv"))

  glimpse(df)

  df |>
    ggplot() +
    aes(x = value, y = report_id) +
    geom_col() +
    facet_wrap(~metric_id) +
    labs(
      title = "Resolution Metrics",
      subtitle = "2023-2018",
      caption = "Source: <add source>",
      x = "applications"
    ) +
    theme_minimal()
}
# resolution_metrics()
