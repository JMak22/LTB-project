member_counts_by_file <- function() {
  library(readr)
  library(tidyr)
  library(ggplot2)

  df <- read_csv(here::here("cleaned_data", "member_counts_by_file.csv"))

  separate_longer_delim(
    data = df,
    cols = names_found,
    delim = "; ",
    # names_sep = "x_",
    # too_few = "align_start"
  ) |>
    mutate(
      file = stringr::str_replace_all(file, "_text.txt", ""),
      file = stringr::str_replace_all(file, "_names.txt", ""),
      file = stringr::str_replace_all(file, "_", "-"),
    ) |>
    ggplot() +
    aes(x = file, y = names_found) +
    geom_tile() +
    scale_x_discrete(sec.axis = dup_axis()) +
    scale_y_discrete(sec.axis = dup_axis()) +
    labs(
      title = "Member Counts by File",
      subtitle = "1998-2009",
      caption = "Source:<add source>"
    ) +
    theme_void() +
    theme(
      axis.text.y.left = element_text(hjust = 1),
      axis.text.y.right = element_text(hjust = 0),
      axis.text.x.bottom = element_text(hjust = 0.5),
      axis.text.x.top = element_text(hjust = 0.5),
    )

  df |>
    mutate(
      n = canonical_names_found -
        part_time_names_found +
        part_time_names_found / 2,
      date = substr(file, 1, 7)
    ) |>
    ggplot() +
    aes(x = date, y = n) +
    geom_point()
}
