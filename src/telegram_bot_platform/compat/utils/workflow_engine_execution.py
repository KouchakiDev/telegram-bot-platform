from __future__ import annotations

from .workflow_engine_context import *


class WorkstationEngineExecutionMixin:
    def _normalize_positions(self) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        visiting, resolved = set(), {}

        def max_numeric() -> int:
            nums = [
                cfg["position"] for cfg in self._flow.values()
                if isinstance(cfg.get("position"), int)
            ]
            return max(nums, default=0)

        def shift_positions(start_pos: int) -> None:
            """Legacy-compatible behavior preserved for this callable."""
            for step, cfg in self._flow.items():
                pos = cfg.get("position")
                if isinstance(pos, int) and pos >= start_pos:
                    cfg["position"] = pos + 1
                    if step in resolved:        # Internal implementation note: legacy behavior is preserved during modernization.
                        resolved[step] = pos + 1

        def resolve(step_name: str) -> int:
            if step_name in resolved:
                return resolved[step_name]
            if step_name in visiting:
                raise StepConfigError(f"Cycle detected around step '{step_name}'")
            if step_name not in self._flow:
                raise StepConfigError(f"Unknown step referenced: '{step_name}'")

            visiting.add(step_name)
            cfg = self._flow[step_name]
            pos = cfg.get("position")

            # Internal implementation note: legacy behavior is preserved during modernization.
            if isinstance(pos, int):
                resolved[step_name] = pos

            # Internal implementation note: legacy behavior is preserved during modernization.
            elif isinstance(pos, str):
                # Internal implementation note: legacy behavior is preserved during modernization.
                if pos.lower() == "end":
                    if "_END_PLACED" in resolved:
                        logger.warning("Extra 'end' position ignored for step '%s'", step_name)
                        candidate = None
                    else:
                        resolved["_END_PLACED"] = True
                        candidate = max_numeric() + 1
                    cfg["position"] = candidate
                    resolved[step_name] = candidate

                # Internal implementation note: legacy behavior is preserved during modernization.
                else:
                    ref_val = resolve(pos)
                    candidate = ref_val + 1
                    shift_positions(candidate)
                    cfg["position"] = candidate
                    resolved[step_name] = candidate


            # Internal implementation note: legacy behavior is preserved during modernization.
            else:
                candidate = max_numeric() + 1
                cfg["position"] = candidate
                resolved[step_name] = candidate

            visiting.remove(step_name)
            return resolved[step_name]

        # Internal implementation note: legacy behavior is preserved during modernization.
        for step in list(self._flow):
            resolve(step)
        # ------------------------------------------------------------------
        # Internal implementation note: legacy behavior is preserved during modernization.
        # Internal implementation note: legacy behavior is preserved during modernization.
        # ------------------------------------------------------------------
        used: dict[int, str] = {}            # Internal implementation note: legacy behavior is preserved during modernization.
        # Internal implementation note: legacy behavior is preserved during modernization.
        for step, cfg in sorted(
            self._flow.items(),
            key=lambda item: (item[1].get("position", 0), item[0]),
        ):
            pos = cfg.get("position")
            if not isinstance(pos, int):
                continue                      # Internal implementation note: legacy behavior is preserved during modernization.
            while pos in used:
                pos += 1                      # Internal implementation note: legacy behavior is preserved during modernization.
            if pos != cfg["position"]:
                logger.debug(
                    "Position collision detected → shifting step '%s' from %d → %d",
                    step, cfg["position"], pos,
                )
                cfg["position"] = pos
            used[pos] = step

    def _first_active_step(self) -> str:
        """Legacy-compatible behavior preserved for this callable."""
        try:
            # Internal implementation note: legacy behavior is preserved during modernization.
            active_steps = [
                (name, cfg) for name, cfg in self._flow.items() if cfg.get("active", True)
            ]

            if not active_steps:
                # Internal implementation note: legacy behavior is preserved during modernization.
                logger.error("No active step found in the workflow.")
                raise StepConfigError("هیچ مرحله فعالی در جریان کاری وجود ندارد.")

            # Internal implementation note: legacy behavior is preserved during modernization.
            return min(active_steps, key=lambda item: item[1].get("position", 0))[0]

        except Exception as exc:  # noqa: BLE001
            # Internal implementation note: legacy behavior is preserved during modernization.
            logger.exception("Unexpected error in _first_active_step: %s", exc)
            raise

    def execute_next(self, user_id: str, message: Any):
        """Legacy-compatible behavior preserved for this callable."""
        try:
            # Internal implementation note: legacy behavior is preserved during modernization.
            step = self._user_states.get(user_id, {}).get("current_step")

            # Internal implementation note: legacy behavior is preserved during modernization.
            if (
                not step
                or step not in self._flow
                or not self._flow[step].get("active", True)
            ):
                step = self._first_active_step()
                # Internal implementation note: legacy behavior is preserved during modernization.
                self._persist(user_id, "current_step", step)
                logger.debug("User %s moved to first active step: %s", user_id, step)

            # Internal implementation note: legacy behavior is preserved during modernization.
            return self.execute_step(user_id, step, message)

        except StepConfigError:
            # Internal implementation note: legacy behavior is preserved during modernization.
            raise

        except Exception as exc:  # noqa: BLE001
            # Internal implementation note: legacy behavior is preserved during modernization.
            logger.exception("Failed to execute next step for user %s: %s", user_id, exc)
            raise

    def _determine_next_step(self, step_conf: Dict[str, Any], user_id: str, response: Any) -> Optional[str]:  # noqa: ANN401
        """Legacy-compatible behavior preserved for this callable."""
        try:
            # Internal implementation note: legacy behavior is preserved during modernization.
            if response is None:
                return None  # Internal implementation note: legacy behavior is preserved during modernization.

            next_fn = step_conf.get("next_step_fn")
            if next_fn:
                if isinstance(next_fn, str):
                    next_fn_callable = getattr(self._target, next_fn)
                else:
                    next_fn_callable = next_fn  # type: ignore[assignment]
                return next_fn_callable(user_id=user_id, response=response)

            # Internal implementation note: legacy behavior is preserved during modernization.
            current_pos = step_conf.get("position", 0)
            # Internal implementation note: legacy behavior is preserved during modernization.
            next_steps = [
                (name, conf)
                for name, conf in self._flow.items()
                if conf.get("position", 0) > current_pos and conf.get("active", True)
            ]
            if not next_steps:
                return None
            # Internal implementation note: legacy behavior is preserved during modernization.
            next_step_name = min(next_steps, key=lambda item: item[1]["position"])[0]
            return next_step_name
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to determine next step: %s", exc, exc_info=True)
            return None

    def execute_step(self, user_id: str, step_name: str, message: Any) -> Any:  # noqa: ANN401
        """Legacy-compatible behavior preserved for this callable."""
        try:
            step_conf = self._flow.get(step_name)
            if step_conf is None:
                raise StepConfigError(f"Step '{step_name}' not found in flow configuration")
            if not step_conf.get("active", True):
                logger.warning("Step '%s' is inactive – skipping.", step_name)
                return self._skip_step(user_id, step_name, reason="inactive")

            # Internal implementation note: legacy behavior is preserved during modernization.
            roles_allowed = step_conf.get("roles_allowed")
            if roles_allowed is not None:
                user_role = self._get_user_role(user_id)
                if user_role not in roles_allowed:
                    logger.warning("User '%s' role '%s' not allowed for step '%s' – skipping.", user_id, user_role, step_name)
                    return self._skip_step(user_id, step_name, reason="role_not_allowed")

            # Internal implementation note: legacy behavior is preserved during modernization.
            cond = step_conf.get("display_condition")
            if cond and not self._evaluate_condition(cond, user_id):
                logger.info("Display condition not met for step '%s' – skipping.", step_name)
                return self._skip_step(user_id, step_name, reason="condition_false")

            # Internal implementation note: legacy behavior is preserved during modernization.
            self._run_hooks(step_conf.get("pre_hooks", []), user_id, step_name, message)

            # Internal implementation note: legacy behavior is preserved during modernization.
            handler = self._get_handler(step_name)
            response = handler(user_id=user_id, message=message)

            # Internal implementation note: legacy behavior is preserved during modernization.
            self._run_hooks(step_conf.get("post_hooks", []), user_id, step_name, message, response)

            # Internal implementation note: legacy behavior is preserved during modernization.
            next_step = self._determine_next_step(step_conf, user_id, response)
            if next_step:
                self._persist(user_id, "current_step", next_step)

            logger.info("Step '%s' executed successfully for user '%s'.", step_name, user_id)
            return response
        except Exception as exc:  # noqa: BLE001
            logger.error("Error while executing step '%s' for user '%s': %s", step_name, user_id, exc, exc_info=True)
            self._handle_step_failure(step_name, user_id, exc)
            raise StepExecutionError(str(exc)) from exc

    def _validate_flow_and_contract(self) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        try:
            missing_steps = self.get_missing_steps()
            if missing_steps:
                raise StepNotImplementedError(f"Missing handler implementation for steps: {missing_steps}")

            unconfigured_steps = self.get_unconfigured_steps()
            if unconfigured_steps:
                logger.warning("Unconfigured steps detected in contract: %s", unconfigured_steps)
        except Exception as exc:  # noqa: BLE001
            logger.error("Flow/contract validation failed: %s", exc, exc_info=True)
            raise

    def _get_handler(self, step_name: str) -> Callable[..., Any]:  # noqa: ANN401
        """Legacy-compatible behavior preserved for this callable."""
        handler = self._contract.get(step_name, {}).get("handler")
        if handler is None:
            raise StepNotImplementedError(f"Handler for step '{step_name}' not implemented")
        return handler

    def _run_hooks(
        self,
        hooks: List[Callable[[str, str, Any, Optional[Any]], None]] | List[str],
        user_id: str,
        step_name: str,
        message: Any,
        response: Any | None = None,
    ) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        for hook in hooks:
            try:
                fn = hook
                if isinstance(hook, str):
                    fn = getattr(self._target, hook)
                if callable(fn):
                    fn(user_id=user_id, step=step_name, message=message, response=response)
            except Exception as exc:  # noqa: BLE001
                logger.error("Hook '%s' failed: %s", hook, exc, exc_info=True)

    def _skip_step(self, user_id: str, step_name: str, *, reason: str) -> None:
        logger.info("Skip step '%s' for user '%s' due to %s.", step_name, user_id, reason)
        step_conf = self._flow[step_name]
        action = step_conf.get("on_skip", "next")

        if action.startswith("jump_to:"):
            dest = action.split(":", 1)[1]
            self._persist(user_id, "current_step", dest)

        elif action == "next":
            # Internal implementation note: legacy behavior is preserved during modernization.
            next_step = self._determine_next_step(step_conf, user_id, response=True)
            if next_step:
                self._persist(user_id, "current_step", next_step)
                return next_step            

        elif action == "fail":
            self._handle_step_failure(step_name, user_id, reason)

    def _handle_step_failure(self, step_name: str, user_id: str, exc: Exception | str) -> None:
        """Legacy-compatible behavior preserved for this callable."""
        step_conf = self._flow.get(step_name, {})
        action = step_conf.get("on_fail", "restart")
        logger.warning("Handling failure for step '%s' with action '%s'", step_name, action)
        if action == "skip":
            self._skip_step(user_id, step_name, reason="failure")
        elif action == "restart":
            self._persist(user_id, "current_step", step_name)  # reset to same step for retry
        elif action == "notify_admin":
            self._notify_admin(step_name, user_id, exc)

    def _evaluate_condition(self, condition: str | Callable[[str], bool], user_id: str) -> bool:
        """Legacy-compatible behavior preserved for this callable."""
        try:
            if callable(condition):
                return bool(condition(user_id=user_id))

            # Internal implementation note: legacy behavior is preserved during modernization.
            local_ctx = {"state": self._user_states.get(user_id, {})}

            return bool(eval(condition, {}, local_ctx))    # noqa: S307
        except Exception as exc:
            logger.error("Condition evaluation failed: %s", exc, exc_info=True)
            return False
