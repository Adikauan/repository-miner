import { render, screen } from "@testing-library/react";
import { expect, it, vi } from "vitest";
import { UnauthorizedCommitList } from "../../src/reporting/UnauthorizedCommitList";

it("renders report items in the API order and exposes no page-size control", () => {
  const onPage = vi.fn();
  render(<UnauthorizedCommitList page={{ offset: 0, limit: 50, items: [
    { id: "alert-new", repository_id: "repo", branch: "main", commit_hash: "newest", author_name: "Synthetic", author_email: null, committed_at: "2026-01-03T00:00:00Z" },
    { id: "alert-old", repository_id: "repo", branch: "main", commit_hash: "oldest", author_name: "Synthetic", author_email: null, committed_at: "2026-01-01T00:00:00Z" },
  ] }} onPage={onPage} />);
  const rows = screen.getAllByRole("row");
  expect(rows[1]).toHaveTextContent("newest");
  expect(rows[2]).toHaveTextContent("oldest");
  expect(screen.queryByRole("combobox")).not.toBeInTheDocument();
});
