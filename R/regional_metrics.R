regional_metrics <- function() {
  library(readr)
  library(ggplot2)
  library(dplyr)
  library(tidyr)
  df <- read_csv(here::here("cleaned_data", "regional_metrics.csv"))

  glimpse(df)

  df |>
    select(-notes) |>
    drop_na() |>
    ggplot() +
    aes(x = value, y = report_id) +
    geom_col(orientation = "y") +
    labs(
      title = "regional metrics",
      subtitle = "1998-2014",
      caption = "Source:<add source>",
      x = "applications"
    ) +
    scale_x_continuous(
      labels = scales::label_number(scale_cut = scales::cut_short_scale())
    ) +
    facet_wrap(~region_id, ncol = 5) +
    theme_minimal()
}

# regional_metrics()
